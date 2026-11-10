"""
Generates the daily GitHub Pages dashboard (`docs/index.html`), daily Markdown report (`docs/DAILY_REPORT.md`),
and sends optional Telegram or Discord notifications if secrets are configured.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import requests


def build_reports_and_notify(results: List[Dict[str, Any]], docs_dir: Path) -> None:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build Markdown Report
    md_lines = [
        "# EquiLogic AI — 365-Day Automated Daily Race Analysis",
        f"**Last Automated Cloud Run:** `{now_utc}` | **Engine:** 9-Rule Conditional Logic + Class 1–6 Specialist Regime",
        "",
        "## Summary of Today's #1 AI Predicted Winners & Value Picks",
        "",
        "| Date & Time | Track & Country | Race & Detected Class | #1 AI Predicted Winner | Win Prob % | Best Value Edge | Pace Shape | Source |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in results:
        val = r.get("best_value_candidate") or {}
        val_str = f"**{val.get('name')}** (+{val.get('value_edge')}% edge)" if val else "N/A"
        md_lines.append(
            f"| `{r['date']} {r['race_time']}` | {r['track']} ({r['country']}) | {r['race_name']} (**Class {r['detected_class']}**) "
            f"| **{r['predicted_winner']}** ({r['winner_score']} pts) | `{r['winner_probability']}%` | {val_str} | {r['pace_tempo']} | [Racecard]({r['source_url']}) |"
        )

    md_lines.append("")
    md_lines.append("## Detailed Horse-by-Horse 9-Rule Breakdown")
    md_lines.append("")
    for r in results:
        md_lines.append(f"### {r['track']} ({r['race_time']}) — {r['race_name']} [Class {r['detected_class']}]")
        md_lines.append(f"- **Going:** {r['going']} | **Distance:** {r['distance_furlongs']}f | **Pace Forecast:** {r['pace_tempo']} | **Source:** [{r['track']} Racecard]({r['source_url']})")
        podium_str = ", ".join(f"{p['rank']}. **{p['name']}** ({p['win_prob']}%)" for p in r["podium"])
        md_lines.append(f"- **Predicted 1-2-3 Podium:** {podium_str}")
        md_lines.append("")
        for hr in r["runners"]:
            md_lines.append(
                f"#### #{hr['number']} {hr['name']} (Rank #{hr['rank']} — Score: `{hr['raw_score']}` | Win Prob: `{hr['win_probability']}%` vs Market `{hr['market_probability']}%` | Confidence: `{hr['confidence_tier']}`)"
            )
            md_lines.append(f"- **Profile:** Draw {hr['draw']} | Weight: {hr['weight']} | OR: {hr['or']} | Form: `{hr['form']}` | Jockey: {hr['jockey']} | Trainer: {hr['trainer']}")
            if hr["green_flags"]:
                md_lines.append("- **Green Flags:** " + " ; ".join(hr["green_flags"]))
            if hr["red_flags"]:
                md_lines.append("- **Red Flags:** " + " ; ".join(hr["red_flags"]))
            md_lines.append("")

    (docs_dir / "DAILY_REPORT.md").write_text("\n".join(md_lines), encoding="utf-8")

    # 2. Build Interactive GitHub Pages HTML Dashboard (`docs/index.html`)
    cards_html = []
    for r in results:
        rows_html = []
        for hr in r["runners"]:
            g_badges = "".join(f"<div class='flag green'>+ {g}</div>" for g in hr["green_flags"])
            r_badges = "".join(f"<div class='flag red'>- {rf}</div>" for rf in hr["red_flags"])
            rows_html.append(f"""
            <tr>
              <td><strong>#{hr['rank']}</strong></td>
              <td><strong>{hr['number']}. {hr['name']}</strong><br><small>{hr['jockey']} / {hr['trainer']}</small></td>
              <td><code>{hr['form']}</code><br><small>OR {hr['or']} | {hr['weight']}</small></td>
              <td><strong>{hr['raw_score']}</strong></td>
              <td><span class='prob'>{hr['win_probability']}%</span><br><small>Mkt: {hr['market_probability']}% (Edge: {hr['value_edge']:+.2f}%)</small></td>
              <td>{g_badges}{r_badges}</td>
            </tr>
            """)
        cards_html.append(f"""
        <div class="race-card">
          <div class="race-header">
            <div>
              <span class="badge">Class {r['detected_class']}</span>
              <span class="badge">{r['country']} • {r['track']}</span>
              <h2>{r['race_time']} — {r['race_name']}</h2>
              <p>Going: <strong>{r['going']}</strong> | Trip: <strong>{r['distance_furlongs']}f</strong> | Pace: <strong>{r['pace_tempo']}</strong> | <a href="{r['source_url']}" target="_blank">Official Source</a></p>
            </div>
            <div class="winner-box">
              <div class="winner-label">#1 AI PREDICTED WINNER</div>
              <div class="winner-name">{r['predicted_winner']}</div>
              <div class="winner-meta">Win Prob: {r['winner_probability']}% | Score: {r['winner_score']}</div>
            </div>
          </div>
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Horse (Jockey / Trainer)</th>
                <th>Form / OR / Wt</th>
                <th>9-Rule Score</th>
                <th>AI Win % vs Market</th>
                <th>9-Rule Green & Red Flags</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows_html)}
            </tbody>
          </table>
        </div>
        """)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>EquiLogic AI — 365-Day Cloud Horse Racing Intelligence</title>
  <style>
    body {{ background: #0b1120; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 24px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
    h1 {{ margin: 0; color: #fbbf24; font-size: 24px; }}
    .race-card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
    .race-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }}
    .badge {{ background: #1e3a8a; color: #93c5fd; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-right: 6px; }}
    .winner-box {{ background: #064e3b; border: 1px solid #10b981; padding: 12px 18px; border-radius: 10px; text-align: right; }}
    .winner-label {{ font-size: 11px; color: #6ee7b7; letter-spacing: 0.08em; font-weight: 700; }}
    .winner-name {{ font-size: 20px; font-weight: 800; color: #ffffff; }}
    .winner-meta {{ font-size: 13px; color: #a7f3d0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #1f2937; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
    .prob {{ font-size: 16px; font-weight: 700; color: #fbbf24; }}
    .flag {{ font-size: 12px; margin-bottom: 3px; padding: 2px 6px; border-radius: 4px; }}
    .flag.green {{ background: rgba(16, 185, 129, 0.15); color: #6ee7b7; }}
    .flag.red {{ background: rgba(239, 68, 68, 0.15); color: #fca5a5; }}
    a {{ color: #38bdf8; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>EquiLogic AI — 365-Day Horse Racing Intelligence</h1>
        <p style="color:#94a3b8;margin:4px 0 0 0;">9-Rule Conditional Engine + Class 1–6 Specialist Regime • Last Cloud Update: {now_utc}</p>
      </div>
    </header>
    {''.join(cards_html)}
  </div>
</body>
</html>"""
    (docs_dir / "index.html").write_text(html_doc, encoding="utf-8")

    # 3. Optional Telegram / Discord Push Notification
    summary_text = f"EquiLogic AI Daily Run ({now_utc})\n" + "\n".join(
        f"- {r['track']} ({r['race_time']}) [Class {r['detected_class']}]: #1 {r['predicted_winner']} ({r['winner_probability']}% win prob)"
        for r in results
    )

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    tg_chat = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if tg_token and tg_chat:
        try:
            requests.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": tg_chat, "text": summary_text},
                timeout=10,
            )
        except Exception as exc:
            print(f"[INFO] Telegram notification skipped: {exc}")

    discord_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if discord_url:
        try:
            requests.post(discord_url, json={"content": summary_text}, timeout=10)
        except Exception as exc:
            print(f"[INFO] Discord notification skipped: {exc}")
