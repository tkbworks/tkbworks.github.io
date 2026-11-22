#!/usr/bin/env python3
"""サイト版ビルダー: items JSON から公開用ページを生成する。
- 締切が今日以降（または締切なし）→ 現行ページ index.html
- 締切が過ぎたもの → archive.html（「締め切り済み」表示で残す）
使い方: python3 build_site.py items-2026-11.json publish/kawasaki_money [YYYY-MM-DD]
"""
import json, sys, html, datetime, os

src, outdir = sys.argv[1], sys.argv[2]
today = datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else datetime.date.today()
d = json.load(open(src))
os.makedirs(outdir, exist_ok=True)
W = ['月', '火', '水', '木', '金', '土', '日']

CSS = """
  body { font-family: sans-serif; margin: 0; background: #f6f5f1; color: #222; }
  header { background: #1f4d3a; color: #fff; padding: 24px 16px; }
  header h1 { font-size: 21px; margin: 0 0 8px; }
  header p { margin: 0; font-size: 13px; opacity: .92; line-height: 1.7; }
  main { max-width: 760px; margin: 0 auto; padding: 16px; }
  .card { background: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }
  .card.past { background: #eeeeea; color: #666; }
  .meta { font-size: 12px; color: #666; margin-bottom: 6px; }
  .badge { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 999px; background: #e8f0ea; color: #1f4d3a; margin-right: 6px; }
  .badge.warn { background: #fdecec; color: #a33; }
  .badge.fee { background: #eef1f8; color: #345; }
  .badge.past { background: #ddd; color: #555; }
  .card h2 { font-size: 16px; margin: 4px 0 6px; }
  .amount { font-weight: bold; font-size: 14px; margin: 4px 0; }
  .deadline { color: #a33; font-weight: bold; font-size: 14px; }
  .card.past .deadline { color: #888; }
  .summary { font-size: 14px; line-height: 1.6; margin: 6px 0; }
  .note { font-size: 12px; color: #555; line-height: 1.6; }
  .link { margin: 8px 0 0; font-size: 13px; }
  .link a { color: #1f4d3a; font-weight: bold; }
  section h3 { font-size: 16px; margin: 24px 0 4px; }
  section .sub { font-size: 12px; color: #666; margin: 0 0 10px; }
  ul { font-size: 13px; line-height: 1.8; padding-left: 18px; }
  footer { font-size: 12px; color: #777; padding: 8px 16px 28px; max-width: 760px; margin: 0 auto; line-height: 1.7; }
  .ad { max-width: 760px; margin: 24px auto 0; padding: 0 16px; text-align: center; }
"""

def card(i, past=False):
    if past:
        badge = '<span class="badge past">締め切り済み</span>'
        cls = 'card past'
    else:
        bcls = 'badge warn' if '締切注意' in i['category'] else ('badge fee' if i['flow'] == 'pay' else 'badge')
        badge = f'<span class="{bcls}">{html.escape(i["category"])}</span>'
        cls = 'card'
    p = [f'<div class="{cls}">',
         f'<div class="meta">{badge}{html.escape(i["area"])}</div>',
         f'<h2>{html.escape(i["title"])}</h2>']
    if i.get('deadline'):
        dt = datetime.date.fromisoformat(i['deadline'])
        p.append(f'<div class="deadline">締切：{dt.month}月{dt.day}日（{W[dt.weekday()]}） — {html.escape(i.get("deadline_note",""))}</div>')
    elif i.get('deadline_note'):
        p.append(f'<p class="note">{html.escape(i["deadline_note"])}</p>')
    p.append(f'<p class="summary">{html.escape(i["summary"])}</p>')
    p.append(f'<p class="amount">{html.escape(i["amount"])}</p>')
    if i.get('url'):
        p.append(f'<p class="link"><a href="{html.escape(i["url"])}" target="_blank" rel="noopener">公式ページで詳細を見る →</a></p>')
    p.append('</div>')
    return '\n    '.join(p)

def is_past(i):
    return i.get('deadline') and datetime.date.fromisoformat(i['deadline']) < today

current = [i for i in d['items'] if not is_past(i)]
past = sorted([i for i in d['items'] if is_past(i)], key=lambda i: i['deadline'], reverse=True)
rec = sorted([i for i in current if i['flow'] == 'receive'], key=lambda i: i['deadline'] or '9999')
pay = sorted([i for i in current if i['flow'] == 'pay'], key=lambda i: i['deadline'] or '9999')
notes = '\n'.join(f'      <li>{html.escape(n)}</li>' for n in d.get('notes', []))
collected = d.get('collected_at', '')

index = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>暮らしの助けになるお金の情報 | 川崎市</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>暮らしの助けになるお金の情報</h1>
  <p>川崎市の給付金・助成金・申込募集など、暮らしに関わるお金の情報を集めたページです。市の広報などから集めて掲載しています。条件や締切は変わることがあるので、申し込みの前に各項目の公式ページで最新情報を確認してください。</p>
</header>
<main>
  <section>
    <h3>もらえる（給付・助成）</h3>
    <p class="sub">お金が入ってくるもの。締切を逃すと損をするものが中心です。</p>
    {chr(10).join('    ' + card(i) for i in rec)}
  </section>
  <section>
    <h3>支払う・申し込む（利用・購入）</h3>
    <p class="sub">お金が出ていくもの。市の制度で、料金が明示されていて、締切があるものだけを載せています。</p>
    {chr(10).join('    ' + card(i) for i in pay)}
  </section>
  <section>
    <h3>今月の手続きメモ</h3>
    <ul>
{notes}
    </ul>
  </section>
  <section>
    <h3>このサイトについて</h3>
    <ul>
      <li>運営：tkbworks（個人で運営しています）</li>
      <li>このサイトは川崎市や各機関の公式サイトではありません。市の広報などをもとに、個人が情報を集めて掲載しています</li>
      <li>制度の内容・申込についての問い合わせは、各項目の公式ページに記載の窓口へお願いします（このサイトではお答えできません）</li>
      <li>更新：毎月、「かわさき市政だより」の発行に合わせて新しい情報を追加します。締切を過ぎた項目は現行リストから外し、「過去の情報」に移して残します</li>
    </ul>
    <p class="link"><a href="./archive.html">過去の情報（締め切り済み）を見る →</a></p>
  </section>
  <section class="ad">
    <!-- A8.net 広告枠: 取得した広告コードをここに貼る。コードが入るまでは何も表示されない -->
    <!-- 広告を載せたら「このサイトについて」に「当サイトはアフィリエイト広告を含みます」旨を1行追加する -->
  </section>
</main>
<footer>
  情報源：川崎市「かわさき市政だより」2026年11月号（全市版・全区版）、各区のお知らせ（2026年11月）／収集日：{collected}<br>
  制度の詳細・最新情報は、各項目の公式ページでご確認ください。<br>
  更新情報は <a href="https://x.com/takabouworks" target="_blank" rel="noopener">X（@TakabouWorks）</a> でもお知らせします。<br>
  <a href="../">暮らし便利帳（トップ）へ戻る</a>
</footer>
</body>
</html>
"""

if past:
    past_cards = chr(10).join('    ' + card(i, past=True) for i in past)
    past_body = f"""    <p class="sub">締切を過ぎた項目です。申し込みはできませんが、同じ制度が来年も同時期に募集されることがあります。次回の目安として残しています。</p>
{past_cards}"""
else:
    past_body = '    <p class="sub">まだ締め切り済みの項目はありません。</p>'

archive = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>過去の情報（締め切り済み）| 暮らしの助けになるお金の情報・川崎市</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>過去の情報（締め切り済み）</h1>
  <p>「暮らしの助けになるお金の情報」（川崎市）の、締切を過ぎた項目の一覧です。</p>
</header>
<main>
  <section>
{past_body}
  </section>
  <p class="link"><a href="./index.html">← 現在募集中の情報に戻る</a></p>
</main>
<footer>
  運営：tkbworks（個人）。このサイトは川崎市や各機関の公式サイトではありません。<br>
  更新情報は <a href="https://x.com/takabouworks" target="_blank" rel="noopener">X（@TakabouWorks）</a> でもお知らせします。<br>
  <a href="../">暮らし便利帳（トップ）へ戻る</a>
</footer>
</body>
</html>
"""

open(os.path.join(outdir, 'index.html'), 'w').write(index)
open(os.path.join(outdir, 'archive.html'), 'w').write(archive)
print(f'current: {len(current)} (receive {len(rec)} / pay {len(pay)}), past: {len(past)}, as of {today}')
