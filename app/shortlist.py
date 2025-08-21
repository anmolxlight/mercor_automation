from datetime import datetime
from . import airtable
from .schema import *
from .config import TIER1_COMPANIES,TARGET_COUNTRIES

def get_error_details(e):
    """Extract detailed error information from Airtable API response"""
    if hasattr(e, 'response') and e.response:
        try:
            error_details = e.response.json()
            return str(error_details)
        except:
            return f"Raw response: {e.response.text}"
    return str(e)
def parse_year(s):
    try:
        return int(str(s)[:4])
    except:
        return None
def years_between(start,end):
    if not start:
        return 0.0
    ys=parse_year(start)
    ye=parse_year(end) if end else datetime.utcnow().year
    if ys is None or ye is None:
        return 0.0
    return max(0.0,ye-ys)
def total_years(experiences):
    return sum(years_between(e.get("start"),e.get("end")) for e in experiences or [])
def worked_tier1(experiences):
    for e in experiences or []:
        c=e.get("company") or ""
        if any(x.lower() in c.lower() for x in TIER1_COMPANIES):
            return True
    return False
def in_target(location):
    if not location:
        return False
    l=location.lower()
    for c in TARGET_COUNTRIES:
        if c.lower() in l:
            return True
    return False
def evaluate(applicant_row,merged):
    personal=merged.get("personal") or {}
    salary=merged.get("salary") or {}
    exps=merged.get("experience") or []
    
    # Calculate criteria
    years_exp = total_years(exps)
    has_tier1 = worked_tier1(exps)
    preferred_rate = salary.get("preferred_rate") or 10**9
    availability = salary.get("availability") or 0
    location = personal.get("location") or "Unknown"
    
    # Evaluate each criteria
    exp_ok = years_exp >= 4.0 or has_tier1
    comp_ok = preferred_rate <= 100 and availability >= 20
    loc_ok = in_target(location)
    
    # Overall decision
    ok = exp_ok and comp_ok and loc_ok
    
    # Generate human-readable reason
    if ok:
        reason_parts = []
        # Experience qualification
        if years_exp >= 4.0 and has_tier1:
            reason_parts.append(f"has {years_exp:.1f} years of experience including Tier 1 companies")
        elif years_exp >= 4.0:
            reason_parts.append(f"has {years_exp:.1f} years of experience")
        elif has_tier1:
            reason_parts.append(f"has worked at a Tier 1 company ({years_exp:.1f} years total exp)")
        
        reason_parts.append(f"rate of ${preferred_rate}/hr is within budget")
        reason_parts.append(f"available {availability} hours/week")
        reason_parts.append(f"located in target region ({location})")
        
        reason = f"SHORTLISTED: Candidate meets all criteria - " + ", ".join(reason_parts) + "."
    else:
        # Explain why not shortlisted
        issues = []
        if not exp_ok:
            if years_exp < 4.0 and not has_tier1:
                issues.append(f"insufficient experience ({years_exp:.1f} years, need 4+ years OR Tier 1 company experience)")
        if not comp_ok:
            if preferred_rate > 100:
                issues.append(f"rate too high (${preferred_rate}/hr, max $100/hr)")
            if availability < 20:
                issues.append(f"low availability ({availability} hrs/week, need 20+ hrs/week)")
        if not loc_ok:
            issues.append(f"location not in target regions ({location})")
        
        reason = f"NOT SHORTLISTED: " + "; ".join(issues) + "."
    
    return ok, reason
def apply_shortlist(applicant_id,merged):
    row=airtable.find_one_by_field(APPLICANTS_TABLE,F_APPLICANT_ID,applicant_id)
    ok,why=evaluate(row,merged)
    if ok:
        import json
        # Create or update shortlist record with proper applicant linking
        try:
            # Check if shortlist record already exists for this applicant
            existing_shortlist = None
            try:
                # Try to find existing shortlist by searching for records that link to this applicant
                all_shortlist = airtable.list_records(SHORTLIST_TABLE)
                for record in all_shortlist:
                    applicant_links = record.get("fields", {}).get(F_SHORTLIST_APPLICANT_LINK, [])
                    if isinstance(applicant_links, list) and any(link.get("id") == row["id"] for link in applicant_links):
                        existing_shortlist = record
                        break
            except:
                pass  # Continue with creation if search fails
            
            # Prepare shortlist data with correct linking format
            shortlist_data = {
                F_SHORTLIST_APPLICANT_LINK: [row["id"]],  # Airtable linked records use just the ID, not nested objects
                F_COMPRESSED_JSON: json.dumps(merged),
                F_SHORTLIST_REASON: why
            }
            
            print(f"DEBUG: Trying to create shortlist record for {applicant_id}")
            print(f"DEBUG: Applicant record ID: {row['id']}")
            
            if existing_shortlist:
                # Update existing shortlist record
                airtable.update_record(SHORTLIST_TABLE, existing_shortlist["id"], {
                    F_COMPRESSED_JSON: json.dumps(merged),
                    F_SHORTLIST_REASON: why
                })
                print(f"SUCCESS: Updated existing shortlist record for {applicant_id}")
            else:
                # Create new shortlist record with all data at once
                try:
                    result = airtable.create_record(SHORTLIST_TABLE, shortlist_data)
                    print(f"SUCCESS: Created shortlist record for {applicant_id} with applicant link")
                except Exception as create_e:
                    print(f"DEBUG: Failed to create with link, error: {get_error_details(create_e)}")
                    # If creation with link fails, try different linking approaches
                    link_formats = [
                        [{"id": row["id"]}],  # Nested object format
                        row["id"],            # Just the ID string
                        [row["id"]]           # Array of ID strings (already tried above)
                    ]
                    
                    created = False
                    for i, link_format in enumerate(link_formats):
                        try:
                            test_data = {
                                F_SHORTLIST_APPLICANT_LINK: link_format,
                                F_COMPRESSED_JSON: json.dumps(merged),
                                F_SHORTLIST_REASON: why
                            }
                            result = airtable.create_record(SHORTLIST_TABLE, test_data)
                            print(f"SUCCESS: Created shortlist record using link format {i+1}")
                            created = True
                            break
                        except Exception as format_e:
                            print(f"DEBUG: Link format {i+1} failed: {get_error_details(format_e)}")
                            continue
                    
                    if not created:
                        # Last resort: create without link and update separately
                        print("DEBUG: Trying fallback approach without initial link")
                        basic_data = {
                            F_COMPRESSED_JSON: json.dumps(merged),
                            F_SHORTLIST_REASON: why
                        }
                        result = airtable.create_record(SHORTLIST_TABLE, basic_data)
                        print(f"SUCCESS: Created basic shortlist record for {applicant_id}")
                        
                        # Try to add the link with different formats
                        link_success = False
                        for i, link_format in enumerate(link_formats):
                            try:
                                airtable.update_record(SHORTLIST_TABLE, result["id"], {
                                    F_SHORTLIST_APPLICANT_LINK: link_format
                                })
                                print(f"SUCCESS: Added applicant link using format {i+1}")
                                link_success = True
                                break
                            except Exception as link_e:
                                print(f"DEBUG: Update with link format {i+1} failed: {get_error_details(link_e)}")
                                continue
                        
                        if not link_success:
                            print(f"WARNING: Could not add applicant link with any format. Record created without link.")
                            # Let's also try some common field name variations
                            field_variations = ["Applicant", "Applicants", "Applicant ID", "ApplicantID"]
                            for field_name in field_variations:
                                for link_format in link_formats:
                                    try:
                                        airtable.update_record(SHORTLIST_TABLE, result["id"], {
                                            field_name: link_format
                                        })
                                        print(f"SUCCESS: Added applicant link using field '{field_name}' with format {link_formats.index(link_format)+1}")
                                        link_success = True
                                        break
                                    except:
                                        continue
                                if link_success:
                                    break
                
        except Exception as e:
            print(f"WARNING: Could not create/update shortlist record: {get_error_details(e)}")
            # Don't fail the entire process if shortlist creation fails
        
        # Update applicant status
        try:
            airtable.update_record(APPLICANTS_TABLE,row["id"],{F_SHORTLIST_STATUS:"Shortlisted"})
        except Exception as e:
            print(f"WARNING: Could not update applicant status to Shortlisted: {e}")
    else:
        try:
            airtable.update_record(APPLICANTS_TABLE,row["id"],{F_SHORTLIST_STATUS:"Not Shortlisted"})
        except Exception as e:
            print(f"WARNING: Could not update applicant status to Not Shortlisted: {e}")
    return ok,why
