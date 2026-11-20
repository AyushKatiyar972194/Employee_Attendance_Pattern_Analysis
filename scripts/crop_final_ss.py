"""Crop and process high-resolution screenshots from SS/Final_SS into presentation and documentation assets."""
import os
from PIL import Image

def crop_box(img_path, box, out_path):
    abs_src = os.path.abspath(img_path)
    abs_out = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(abs_out), exist_ok=True)
    im = Image.open(abs_src)
    cropped = im.crop(box)
    cropped.save(abs_out, "PNG", optimize=True)
    print(f"Saved: {out_path} {cropped.size} from {os.path.basename(img_path)}")

def main():
    crops_dir = "SS/slides_crops"
    ss_dir = "SS/Final_SS"
    os.makedirs(crops_dir, exist_ok=True)

    # 1. Slide 7: Executive Header Banner + Flash Briefing
    # x: 80 to 1840, y: 140 to 470
    crop_box(
        f"{ss_dir}/Workforce Intelligence — Northstar Technologies.png",
        (80, 140, 1840, 470),
        f"{crops_dir}/ov_banner_kpis.png"
    )

    # 2. Slide 8: Workforce Dynamics - Daily Trends & Presence Breakdown
    # x: 80 to 1840, y: 680 to 1510
    crop_box(
        f"{ss_dir}/Executive Overview — Northstar Analytics.png",
        (80, 680, 1840, 1510),
        f"{crops_dir}/ov_trends_breakdown.png"
    )

    # 3. Slide 9: Department Benchmarks - Fulfillment Chart & Quadrant Matrix
    # x: 80 to 1840, y: 505 to 1500
    crop_box(
        f"{ss_dir}/Department Benchmarks — Northstar Analytics.png",
        (80, 505, 1840, 1500),
        f"{crops_dir}/dept_chart_baseline.png"
    )

    # 4. Slide 10: Punctuality Histogram & Grace Period Cutoff (09:10 AM)
    # x: 80 to 1840, y: 505 to 1460
    crop_box(
        f"{ss_dir}/Punctuality & Time Analysis — Northstar Analytics.png",
        (80, 505, 1840, 1460),
        f"{crops_dir}/time_hist_grace.png"
    )

    # 5. Slide 11: Top Chronic Late Arrivals & Punctuality Leaderboard
    # x: 80 to 1840, y: 1000 to 1950
    crop_box(
        f"{ss_dir}/Punctuality & Time Analysis — Northstar Analytics (1).png",
        (80, 1000, 1840, 1950),
        f"{crops_dir}/time_outlier_callout.png"
    )

    # 6. Slide 12: Data Quality Scorecard - 6 Dimensions Audit
    # x: 80 to 1840, y: 505 to 1260
    crop_box(
        f"{ss_dir}/Data Quality & Records — Northstar Analytics.png",
        (80, 505, 1840, 1260),
        f"{crops_dir}/dq_scorecard.png"
    )

    # 7. Slide 13: Data Ingestion & Missing Punch Remediation Portal
    # x: 80 to 1840, y: 1380 to 2480
    crop_box(
        f"{ss_dir}/Data Quality & Records — Northstar Analytics.png",
        (80, 1380, 1840, 2480),
        f"{crops_dir}/dq_pipeline_runs.png"
    )

    # Additional high-value crops for presentation and docs:
    # 8. Department Performance Scorecards (Grades A+, A, C)
    crop_box(
        f"{ss_dir}/Workforce Intelligence — Northstar Technologies.png",
        (80, 1400, 1840, 2150),
        f"{crops_dir}/dept_grades_scorecard.png"
    )

    # 9. Predictive Risk Watchlist & Anomaly Detection
    crop_box(
        f"{ss_dir}/Smart Patterns & Policy — Northstar Analytics.png",
        (80, 420, 1840, 1350),
        f"{crops_dir}/predictive_risk_watchlist.png"
    )

    # 10. Policy Lab: 15-Minute Grace Policy Simulation & $42k Cost Recovery
    crop_box(
        f"{ss_dir}/Smart Patterns & Policy — Northstar Analytics.png",
        (80, 1350, 1840, 2400),
        f"{crops_dir}/policy_sensitivity_lab.png"
    )

    # 11. Supervisor 1-on-1 Actionable Discussion Dossier
    crop_box(
        f"{ss_dir}/Workforce Intelligence — Northstar Technologies.png",
        (80, 2080, 1840, 2600),
        f"{crops_dir}/supervisor_1on1_dossier.png"
    )

    # 12. Also copy full screenshots to SS/ for easy direct reference
    import shutil
    pages_map = {
        "Executive_Command_Center_Live.png": f"{ss_dir}/Workforce Intelligence — Northstar Technologies.png",
        "Overview_Workforce_Dynamics_Live.png": f"{ss_dir}/Executive Overview — Northstar Analytics.png",
        "Department_Benchmarks_Live.png": f"{ss_dir}/Department Benchmarks — Northstar Analytics.png",
        "Punctuality_Time_Forensics_Live.png": f"{ss_dir}/Punctuality & Time Analysis — Northstar Analytics.png",
        "Data_Quality_Ingestion_Live.png": f"{ss_dir}/Data Quality & Records — Northstar Analytics.png",
        "Pattern_Intelligence_Policy_Live.png": f"{ss_dir}/Smart Patterns & Policy — Northstar Analytics.png",
    }
    for dest, src in pages_map.items():
        shutil.copy2(src, f"SS/{dest}")
        print(f"Copied full page to SS/{dest}")

if __name__ == "__main__":
    main()
