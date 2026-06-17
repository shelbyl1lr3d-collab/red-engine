#!/usr/bin/env python3
"""
Red Engine V2 — Web UI Dashboard (Full Implementation)
"""
import os, sys, json, subprocess, re, uuid, html as html_mod, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
ENGINE_SCRIPT = str(Path(__file__).parent.parent / "main.py")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Red Engine V2</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0a0a0a; color:#eee; font-family:monospace; display:flex; height:100vh; }
    .sidebar { width:260px; background:#111; border-right:2px solid #ff3333; padding:12px; display:flex; flex-direction:column; overflow-y:auto; }
    .sidebar h1 { color:#ff3333; font-size:16px; margin-bottom:4px; }
    .sidebar .subtitle { color:#666; font-size:11px; margin-bottom:12px; }
    .sidebar button { background:#1a1a1a; color:#ddd; border:1px solid #333; padding:8px 10px; margin-bottom:4px; cursor:pointer; font:inherit; font-size:12px; border-radius:4px; text-align:left; transition:0.15s; width:100%; }
    .sidebar button:hover { background:#ff3333; color:#000; border-color:#ff3333; }
    .sidebar .section { color:#ff9800; font-size:11px; margin:8px 0 4px 0; text-transform:uppercase; letter-spacing:1px; }
    .main { flex:1; display:flex; flex-direction:column; min-width:0; }
    #output { flex:1; padding:16px; overflow-y:auto; font-size:13px; line-height:1.5; }
    #output .log { color:#888; }
    #output .ok { color:#4caf50; }
    #output .err { color:#ff5252; }
    #output .link { color:#4fc3f7; text-decoration:none; display:block; margin:2px 0; }
    #input-row { display:flex; border-top:2px solid #ff3333; }
    #input { flex:1; background:#111; color:#eee; border:none; padding:12px 15px; font:inherit; font-size:13px; outline:none; }
    #send { background:#ff3333; color:#000; border:none; padding:12px 24px; font:inherit; font-weight:bold; cursor:pointer; }
    #send:hover { background:#cc0000; }
    .card { background:#111; border:1px solid #333; border-radius:6px; padding:12px; margin:6px 0; word-break:break-word; }
    .card h3 { color:#ff9800; font-size:14px; margin-bottom:8px; }
    .card h4 { color:#4fc3f7; font-size:13px; margin:6px 0; }
    .card .row { display:flex; justify-content:space-between; margin:3px 0; font-size:12px; }
    .badge { display:inline-block; padding:2px 8px; border-radius:8px; font-size:10px; }
    .badge-green { background:#1a3a1a; color:#4caf50; }
    .badge-red { background:#3a1a1a; color:#ff5252; }
    .badge-gold { background:#3a3a00; color:#ffd700; }
    table { width:100%; border-collapse:collapse; font-size:12px; }
    th, td { padding:6px 8px; text-align:left; border-bottom:1px solid #222; }
    th { color:#ff9800; }
    .pre-wrap { white-space:pre-wrap; font-size:11px; color:#aaa; }
    @media (max-width:768px) { .sidebar { display:none; } body { flex-direction:column; } #output { font-size:12px; } }
  </style>
</head>
<body>
  <div class="sidebar">
    <h1>RED ENGINE V2</h1>
    <div class="subtitle">$5 → $1B → Vessel</div>

    <div class="section">System</div>
    <button onclick="send({command:'status'})">🤖 Family Status</button>
    <button onclick="send({command:'weekly'})">📊 Weekly Report</button>
    <button onclick="send({command:'milestone_check'})">🎯 $1B Milestone</button>

    <div class="section">Chat</div>
    <button onclick="chatMember('Red')">🔴 Red</button>
    <button onclick="chatMember('Scout')">🔭 Scout</button>
    <button onclick="chatMember('Forge')">🔨 Forge</button>
    <button onclick="chatMember('Nexus')">🧮 Nexus</button>
    <button onclick="chatMember('Jobs')">💼 Jobs</button>
    <button onclick="chatMember('Psyche')">🧠 Psyche</button>

    <div class="section">🧠 Family Mind</div>
    <button onclick="send({command:'family_overseer'})">👁️ Overseer Report</button>
    <button onclick="send({command:'family_naming'})">🏛️ Family Naming</button>
    <button onclick="solveUI()">🧮 Solve Problem</button>
    <button onclick="codeUI()">💻 Generate Code</button>
    <button onclick="geniusUI()">🤯 Ask Genius</button>
    <button onclick="send({command:'family_word'})">📖 Word of the Day</button>
    <button onclick="send({command:'family_evolve'})">🔄 Evolve All</button>
    <button onclick="send({command:'family_recalibrate'})">⚙️ Recalibrate</button>
    <button onclick="send({command:'family_upgrade', type:'deep'})">⬆️ Deep Upgrade</button>

    <div class="section">🪙 Agent Coins</div>
    <button onclick="send({command:'family_coin', action:'report'})">💰 Coin Report</button>
    <button onclick="mintCoinUI()">🪙 Mint Agent Coin</button>
    <button onclick="addLiqUI()">💧 Add Liquidity</button>
    <button onclick="gainLiqUI()">📈 Gain Liquidity</button>

    <div class="section">💰 Earn Money</div>
    <button onclick="send({command:'family_income', action:'scan'})">🔍 Scan All Opportunities</button>
    <button onclick="send({command:'family_income', action:'execute'})">⚡ Execute All</button>
    <button onclick="send({command:'family_income', action:'report'})">📊 Income Report</button>
    <button onclick="pipelineUI()">📦 Activate Pipeline</button>
    <button onclick="affiliateUI()">🔗 Find Affiliate Offer</button>
    <button onclick="send({command:'family_affiliate', niche:'crypto'})">🪙 Crypto Affiliate</button>
    <button onclick="send({command:'family_affiliate', niche:'business'})">💼 Biz Affiliate</button>
    <button onclick="send({command:'family_affiliate', niche:'tech'})">💻 Tech Affiliate</button>
    <button onclick="send({command:'scan_all', category:'jobs'})">💼 Scan Jobs</button>
    <button onclick="send({command:'scan_all', category:'crypto'})">🪙 Crypto Bonuses</button>
    <button onclick="send({command:'family_profit', target:'$1B', amount:1000000000})">🎯 $1B Target</button>

    <div class="section">🪂 Airdrops</div>
    <button onclick="send({command:'family_airdrop', action:'live'})">🌍 Live Airdrops</button>
    <button onclick="walletUI()">👛 Set Wallet</button>
    <button onclick="send({command:'family_airdrop', action:'check'})">✅ Check Wallet</button>
    <button onclick="airdropTaskUI()">📋 Airdrop Tasks</button>

    <div class="section">🔎 Web</div>
    <button onclick="searchUI()">🔍 Search Web</button>
    <button onclick="send({command:'family_sync', folder:'/mnt/gdrive/RedEngine'})">☁️ Sync to Drive</button>
    <button onclick="send({command:'family_protect', enable:true})">🛡️ Enable Protection</button>

    <div class="section">🌌 Clusters</div>
    <button onclick="send({command:'family_cluster', action:'discover'})">🛸 Discover Cluster</button>
    <button onclick="send({command:'family_cluster', action:'list'})">📋 List Clusters</button>
    <button onclick="adoptUI()">🤝 Adopt Member</button>

    <div class="section">🔒 Security</div>
    <button onclick="send({command:'family_fraud', message:'test message'})">🔐 Test Fraud Detection</button>

    <div class="section">Game Factory</div>
    <button onclick="send({command:'reskin'})">🎮 Generate 1 Game</button>
    <button onclick="send({command:'forge', count:3})">🎮🎮 Generate 3</button>
    <button onclick="send({command:'forge', count:5})">🎮🎮🎮 Generate 5</button>
    <button onclick="send({command:'deploy'})">🚀 Deploy to Cloud</button>

    <div class="section">Tokens & Finance</div>
    <button onclick="tokenUI()">🪙 Mint Token</button>
    <button onclick="send({command:'tokens_list'})">💰 All Tokens</button>
    <button onclick="send({command:'treasury_report'})">🏦 Treasury</button>
    <button onclick="send({command:'liquidity_report'})">💧 Liquidity Pools</button>
    <button onclick="send({command:'route_revenue', source:'Web UI', amount:100})">🔄 Route $100 Revenue</button>

    <div class="section">Exchange</div>
    <button onclick="send({command:'balance'})">💰 Check Balance</button>
    <button onclick="tradeUI()">📈 Execute Trade</button>

    <div class="section">Tournament</div>
    <button onclick="send({command:'tournament_round'})">🏆 Run Round</button>
    <button onclick="send({command:'tournament_leaderboard'})">📋 Leaderboard</button>
    <button onclick="send({command:'tournament_start', interval:300})">🔄 Auto-Start</button>

    <div class="section">Search & Scan</div>
    <button onclick="send({command:'scan_all', category:'all'})">🔍 Scan All</button>
    <button onclick="send({command:'scan_all', category:'jobs'})">💼 Scan Jobs</button>
    <button onclick="send({command:'scan_all', category:'crypto'})">🪙 Crypto Bonuses</button>
    <button onclick="send({command:'science', topic:'general'})">🔬 Science</button>
    <button onclick="send({command:'science', topic:'neuralink'})">🧠 Neuralink</button>

    <div class="section">Media</div>
    <button onclick="send({command:'media_test'})">🎬 Test Music Video</button>
    <button onclick="send({command:'media_stats'})">📺 YouTube Stats</button>

    <div class="section">Data</div>
    <button onclick="send({command:'notifications'})">📬 Notifications</button>
    <button onclick="send({command:'log'})">📋 Transaction Log</button>

    <div style="flex:1"></div>
    <div style="font-size:10px;color:#555;margin-top:8px">Red Engine V2 — All systems autonomous</div>
  </div>

  <div class="main">
    <div id="output">
      <div style="color:#ff3333;font-size:16px;font-weight:bold;margin-bottom:8px">RED ENGINE V2 — AI FAMILY</div>
      <div style="color:#888;margin-bottom:12px">Vision: $5 → $1B → Vessel → Safety → Evolve daily</div>
      <div id="output-content"></div>
    </div>
    <div id="input-row">
      <input id="input" placeholder="Type command or question...">
      <button id="send" onclick="doSend()">SEND</button>
    </div>
  </div>

  <script>
    const out = document.getElementById('output-content');

    function log(msg, cls='log') {
      out.innerHTML += '<div class="' + cls + '">&gt; ' + msg.replace(/</g,'&lt;') + '</div>';
      out.parentElement.scrollTop = out.parentElement.scrollHeight;
    }

    function send(payload) {
      log(JSON.stringify(payload));
      fetch('/api', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      }).then(r => r.json()).then(d => renderResponse(d))
        .catch(e => log('Error: ' + e.message, 'err'));
    }

    function renderCard(title, content) {
      out.innerHTML += '<div class="card"><h3>' + title + '</h3>' + content + '</div>';
      out.parentElement.scrollTop = out.parentElement.scrollHeight;
    }

    function renderResponse(d) {
      if (d.family) {
        let h = '<div style="margin-bottom:8px">' + d.online + '/' + d.total_members + ' online</div>';
        (d.members || []).forEach(m => {
          const dot = m.status === 'online' ? '#4caf50' : '#666';
          h += '<div class="row"><span><span style="color:' + dot + '">●</span> ' + (m.emoji||'') + ' <b>' + m.name + '</b> <span style="color:#888">- ' + m.role + '</span></span><span style="color:#666">msgs: ' + (m.messages||0) + '</span></div>';
        });
        renderCard('🤖 AI Family', h);
        return;
      }

      if (d.member && d.reply) {
        renderCard((d.emoji||'') + ' ' + d.member + ' <span style="color:#888;font-size:11px">(' + (d.role||'') + ')</span>', '<div>' + d.reply + '</div>');
        return;
      }

      if (d.milestone_reached !== undefined) {
        if (d.milestone_reached) {
          renderCard('🚨 $1B MILESTONE REACHED!', '<div class="row"><span>Balance:</span><span style="color:#4caf50;font-size:16px">$' + d.balance.toLocaleString() + '</span></div><div class="row"><span>Approval:</span><span>' + (d.approval_required ? 'Human required' : 'Auto') + '</span></div><div style="margin-top:8px;color:#888;font-size:11px">' + (d.instructions||'') + '</div>');
        } else {
          renderCard('🎯 Milestone Progress', '<div class="row"><span>Balance:</span><span style="color:#4caf50">$' + (d.balance||0).toLocaleString() + '</span></div><div class="row"><span>Goal:</span><span style="color:#ffd700">$' + (d.goal||'1,000,000,000').toLocaleString() + '</span></div><div class="row"><span>Remaining:</span><span style="color:#ff9800">$' + (d.remaining||0).toLocaleString() + '</span></div><div class="row"><span>Progress:</span><span>' + (d.progress_pct||0) + '%</span></div>');
        }
        return;
      }

      if (d.generated !== undefined && d.games) {
        let h = '<div class="row"><span>Generated:</span><span style="color:#4caf50">' + d.generated + ' games</span></div>';
        (d.games||[]).forEach(g => {
          h += '<div class="row"><span>' + (g.title||g.name||'Game') + '</span><span class="badge badge-gold">' + (g.token_symbol||g.token||'') + '</span></div>';
        });
        renderCard('🎮 Games Generated', h);
        return;
      }

      if (d.deployed !== undefined && d.games) {
        let h = '<div class="row"><span>Deployed:</span><span style="color:#4caf50">' + d.deployed + '</span></div>';
        (d.games||[]).forEach(g => {
          h += '<div style="margin-top:6px"><b>' + (g.game||'Game') + '</b>';
          if (g.github && g.github.deploy_url) h += '<br><a class="link" href="' + g.github.deploy_url + '" target="_blank">' + g.github.deploy_url + '</a>';
          if (g.netlify && g.netlify.url) h += '<br><a class="link" href="' + g.netlify.url + '" target="_blank">' + g.netlify.url + '</a>';
          h += '</div>';
        });
        renderCard('🚀 Deployment Results', h);
        return;
      }

      if (d.tokens && d.count !== undefined) {
        let h = '<div class="row"><span>Total Tokens:</span><span style="color:#ff9800">' + d.count + '</span></div>';
        h += '<div class="row"><span>Total Supply:</span><span>' + (d.total_supply||0).toLocaleString() + '</span></div>';
        h += '<div class="row"><span>Total Liquidity:</span><span>$' + (d.total_liquidity||0).toLocaleString() + '</span></div>';
        h += '<table><tr><th>Name</th><th>Symbol</th><th>Supply</th><th>Liq</th></tr>';
        (d.tokens||[]).forEach(t => { h += '<tr><td>' + t.name + '</td><td style="color:#ff9800">' + t.symbol + '</td><td>' + (t.supply||0).toLocaleString() + '</td><td>$' + (t.liquidity||0) + '</td></tr>'; });
        h += '</table>';
        renderCard('💰 All Tokens', h);
        return;
      }

      if (d.balance !== undefined && typeof d.balance === 'number') {
        renderCard('💰 Balance', '<div class="row"><span>Balance:</span><span style="color:#4caf50;font-size:18px">$' + d.balance.toLocaleString() + '</span></div>');
        return;
      }

      if (d.balance && typeof d.balance === 'object') {
        let h = '';
        if (d.balance.luno) {
          h += '<h4>Luno</h4>';
          (d.balance.luno.balances||[]).forEach(b => { h += '<div class="row"><span>' + b.asset + '</span><span>' + b.balance + '</span></div>'; });
        }
        if (d.balance.treasury) {
          h += '<h4>Treasury</h4>';
          h += '<div class="row"><span>Balance:</span><span>$' + d.balance.treasury.balance + '</span></div>';
          h += '<div class="row"><span>Yield:</span><span>$' + d.balance.treasury.yield + '</span></div>';
        }
        if (d.balance.note) h += '<div style="color:#888">' + d.balance.note + '</div>';
        renderCard('💰 ' + (d.exchange||'Balances'), h || '<div style="color:#888">No balance data</div>');
        return;
      }

      if (d.deployed !== undefined) {
        renderCard('🚀 Deploy Results', '<pre class="pre-wrap">' + JSON.stringify(d, null, 2) + '</pre>');
        return;
      }

      if (d.leaderboard) {
        let h = '<table><tr><th>Rank</th><th>Agent</th><th>Score</th><th>Wins</th><th>Rounds</th></tr>';
        (d.leaderboard||[]).forEach((l, i) => {
          h += '<tr><td>#' + (i+1) + '</td><td style="color:#ff9800">' + l.name + '</td><td>' + (l.total_score||0) + '</td><td>' + (l.wins||0) + '</td><td>' + (l.rounds||0) + '</td></tr>';
        });
        h += '</table>';
        h += '<div style="color:#888;font-size:11px;margin-top:6px">Season ' + (d.season||1) + ' — ' + (d.rounds||0) + ' rounds</div>';
        renderCard('🏆 Tournament Leaderboard', h);
        return;
      }

      if (d.round !== undefined && d.winner) {
        let h = '<div class="row"><span>Round:</span><span style="color:#ff9800">#' + d.round + '</span></div>';
        h += '<div class="row"><span>Winner:</span><span style="color:#4caf50;font-size:16px">' + d.winner + '</span></div>';
        h += '<table><tr><th>Rank</th><th>Agent</th><th>Score</th></tr>';
        (d.rankings||[]).forEach((r, i) => {
          h += '<tr><td>#' + (i+1) + '</td><td>' + r[0] + '</td><td style="color:' + (i===0?'#4caf50':'#eee') + '">' + r[1].toFixed(2) + '</td></tr>';
        });
        h += '</table>';
        renderCard('🏆 Tournament Round ' + d.round, h);
        return;
      }

      if (d.results && Array.isArray(d.results)) {
        let h = '<div class="row"><span>Found:</span><span style="color:#4caf50">' + d.count + ' results</span></div>';
        (d.results||[]).forEach(r => {
          if (r.url) h += '<a class="link" href="' + r.url + '" target="_blank">' + (r.title||'Link') + '</a>';
          if (r.snippet) h += '<div style="color:#888;font-size:11px;margin:2px 0 6px 16px">' + r.snippet.slice(0,150) + '</div>';
        });
        renderCard('🔍 ' + (d.query||'Search Results'), h);
        return;
      }

      if (d.path && (d.path.endsWith('.mp4') || d.path.endsWith('.wav'))) {
        let h = '<div class="row"><span>Path:</span><span style="color:#4caf50">' + d.path + '</span></div>';
        if (d.title) h += '<div class="row"><span>Title:</span><span>' + d.title + '</span></div>';
        if (d.duration_sec) h += '<div class="row"><span>Duration:</span><span>' + d.duration_sec + 's</span></div>';
        renderCard('🎬 Media Generated', h);
        return;
      }

      if (d.title && d.token_symbol) {
        renderCard('🎮 ' + d.title, '<div class="row"><span>Template:</span><span>' + (d.template||'') + '</span></div><div class="row"><span>Theme:</span><span>' + (d.theme||'') + '</span></div><div class="row"><span>Token:</span><span class="badge badge-gold">' + d.token_symbol + '</span></div><div class="row"><span>Path:</span><span style="color:#888;font-size:11px">' + d.path + '</span></div>');
        return;
      }

      if (d.name && d.symbol && d.supply) {
        renderCard('🪙 Token Minted', '<div class="row"><span>Name:</span><span style="color:#ff9800">' + d.name + '</span></div><div class="row"><span>Symbol:</span><span style="color:#ff9800">' + d.symbol + '</span></div><div class="row"><span>Supply:</span><span>' + (d.supply||0).toLocaleString() + '</span></div><div class="row"><span>Chain:</span><span>' + (d.chain||'bsc') + '</span></div><div class="row"><span>Contract:</span><span style="font-size:10px;color:#888">' + (d.contract_address||'') + '</span></div>');
        return;
      }

      if (d.total_routed !== undefined) {
        renderCard('🔄 Revenue Route', '<div class="row"><span>Source:</span><span>' + (d.source||'') + '</span></div><div class="row"><span>Amount:</span><span style="color:#4caf50">$' + d.amount + '</span></div><div class="row"><span>Total Routed:</span><span>$' + d.total_routed + '</span></div>');
        return;
      }

      if (d.notifications) {
        let h = '<div class="row"><span>Count:</span><span>' + d.notifications.length + '</span></div>';
        (d.notifications||[]).slice(0,10).forEach(n => {
          h += '<div style="margin:6px 0;padding:6px;background:#0a0a0a;border-radius:4px">';
          h += '<div style="color:#ff9800;font-size:12px">' + (n.title||'') + '</div>';
          h += '<div style="color:#aaa;font-size:11px">' + (n.message||'') + '</div>';
          h += '<div style="color:#555;font-size:10px">' + (n.time||'') + ' — ' + (n.sender||'') + '</div>';
          h += '</div>';
        });
        renderCard('📬 Notifications', h);
        return;
      }

      if (d.transactions) {
        let h = '<div class="row"><span>Count:</span><span>' + d.transactions.length + '</span></div>';
        (d.transactions||[]).slice(0,10).forEach(t => {
          h += '<div style="margin:4px 0;color:#888;font-size:11px">[' + (t.type||'') + '] ' + (t.detail||'') + ' ' + (t.amount?'$'+t.amount:'') + '</div>';
        });
        renderCard('📋 Transaction Log', h);
        return;
      }

      if (d.pools) {
        let h = '<div class="row"><span>Total Pools:</span><span>' + d.count + '</span></div>';
        h += '<div class="row"><span>Total TVL:</span><span>$' + (d.total_tvl||0) + '</span></div>';
        (d.pools||[]).forEach(p => {
          h += '<div style="margin:6px 0;padding:6px;background:#0a0a0a;border-radius:4px">';
          h += '<div style="color:#4fc3f7;font-size:12px">' + p.id + '</div>';
          h += '<div class="row"><span>Liquidity:</span><span>$' + (p.liquidity||0) + '</span></div>';
          h += '<div class="row"><span>TVL:</span><span>$' + (p.tvl||0) + '</span></div>';
          h += '</div>';
        });
        renderCard('💧 Liquidity Pools', h);
        return;
      }

      if (d.compounded) {
        renderCard('🏦 Treasury Report', '<div class="row"><span>Balance:</span><span style="color:#4caf50;font-size:16px">$' + (d.balance||0).toLocaleString() + '</span></div><div class="row"><span>Compounded:</span><span style="color:#ff9800">$' + (d.compounded.yield||0) + '</span></div><div class="row"><span>Total Deposits:</span><span>$' + (d.total_deposits||0) + '</span></div><div class="row"><span>Yield Earned:</span><span>$' + (d.yield_earned||0) + '</span></div><div class="row"><span>Progress:</span><span>' + (d.progress_pct||0) + '%</span></div>');
        return;
      }

      if (d.project && d.tasks) {
        let h = '<div class="row"><span>Project:</span><span style="color:#ff9800;font-size:14px">' + d.project + '</span></div>';
        if (d.url) h += '<a class="link" href="' + d.url + '" target="_blank">' + d.url + '</a>';
        h += '<div style="margin-top:10px;color:#ff9800;font-weight:bold">📝 Copy-paste these:</div>';
        if (d.tasks.twitter) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #1da1f2"><div style="color:#1da1f2;font-size:11px">TWITTER TASKS</div><div style="font-size:11px;color:#ccc;margin-top:4px;white-space:pre-wrap">' + d.tasks.twitter + '</div></div>';
        if (d.tasks.discord) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #5865f2"><div style="color:#5865f2;font-size:11px">DISCORD</div><div style="font-size:11px;color:#ccc;margin-top:4px;white-space:pre-wrap">' + d.tasks.discord + '</div></div>';
        if (d.tasks.telegram) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #0088cc"><div style="color:#0088cc;font-size:11px">TELEGRAM</div><div style="font-size:11px;color:#ccc;margin-top:4px;white-space:pre-wrap">' + d.tasks.telegram + '</div></div>';
        if (d.tasks.tweet_post) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #1da1f2"><div style="color:#1da1f2;font-size:11px">TWEET TO POST</div><div style="font-size:11px;color:#ccc;margin-top:4px;white-space:pre-wrap">' + d.tasks.tweet_post + '</div></div>';
        if (d.tasks.medium_article) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #00ab6c"><div style="color:#00ab6c;font-size:11px">MEDIUM ARTICLE</div><div style="font-size:11px;color:#ccc;margin-top:4px;white-space:pre-wrap">' + d.tasks.medium_article + '</div></div>';
        h += '<div style="margin-top:10px;color:#4caf50;font-weight:bold">✅ Checklist:</div>';
        (d.checklist||[]).forEach(function(c) { h += '<div style="font-size:11px;color:#aaa;margin:2px 0">' + c + '</div>'; });
        if (d.earn_estimate) h += '<div style="margin-top:8px;color:#ff9800;font-size:11px">💡 ' + d.earn_estimate + '</div>';
        renderCard('📋 Airdrop Tasks — ' + d.project, h);
        return;
      }

      if (d.product && d.promo_content) {
        let h = '<div class="row"><span>Product:</span><span style="color:#ff9800">' + d.product.name + '</span></div>';
        h += '<div class="row"><span>Commission:</span><span style="color:#4caf50">' + d.product.commission + '</span></div>';
        h += '<div class="row"><span>Price:</span><span>$' + d.product.price + '</span></div>';
        h += '<div class="row"><span>Network:</span><span style="color:#4fc3f7">' + d.product.network + '</span></div>';
        h += '<div class="row"><span>Earn/sale:</span><span style="color:#4caf50;font-size:16px">' + d.earn_per_sale + '</span></div>';
        h += '<div style="margin-top:10px"><a class="link" href="' + d.signup_link + '" target="_blank">🔗 Sign up at ' + d.product.network + '</a></div>';
        h += '<div style="margin-top:8px;margin-bottom:4px;color:#ff9800;font-weight:bold">📝 Copy-paste these:</div>';
        if (d.promo_content.reddit_post) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #ff4500"><div style="color:#ff4500;font-size:11px">REDDIT POST</div><div style="font-size:11px;color:#ccc;margin-top:4px">' + d.promo_content.reddit_post.replace(/\n/g,'<br>') + '</div></div>';
        if (d.promo_content.tweet) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #1da1f2"><div style="color:#1da1f2;font-size:11px">TWITTER/X</div><div style="font-size:11px;color:#ccc;margin-top:4px">' + d.promo_content.tweet + '</div></div>';
        if (d.promo_content.medium_headline) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #00ab6c"><div style="color:#00ab6c;font-size:11px">MEDIUM HEADLINE</div><div style="font-size:11px;color:#ccc;margin-top:4px">' + d.promo_content.medium_headline + '</div></div>';
        if (d.promo_content.discord_msg) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #5865f2"><div style="color:#5865f2;font-size:11px">DISCORD</div><div style="font-size:11px;color:#ccc;margin-top:4px">' + d.promo_content.discord_msg + '</div></div>';
        if (d.promo_content.facebook_post) h += '<div style="margin-top:6px;background:#0a0a0a;padding:8px;border-radius:4px;border-left:3px solid #1877f2"><div style="color:#1877f2;font-size:11px">FACEBOOK</div><div style="font-size:11px;color:#ccc;margin-top:4px">' + d.promo_content.facebook_post + '</div></div>';
        h += '<div style="margin-top:10px;color:#888;font-size:11px">Platforms: ' + d.platforms.join(', ') + '</div>';
        renderCard('🔗 Affiliate Offer — $' + d.earn_per_sale + '/sale', h);
        return;
      }

      if (d.ceremony && d.winner) {
        let h = '<div style="text-align:center;margin-bottom:12px"><span style="font-size:32px">🏛️</span></div>';
        h += '<div style="text-align:center;font-size:18px;color:#ffd700;font-weight:bold;margin-bottom:8px">The Family Has Chosen!</div>';
        h += '<div style="text-align:center;font-size:14px;margin-bottom:12px">' + d.winner.emoji + ' <span style="color:#4caf50;font-size:20px;font-weight:bold">' + d.winner.name + '</span> ' + d.winner.emoji + '</div>';
        h += '<div style="text-align:center;color:#aaa;font-size:12px;margin-bottom:12px;font-style:italic">"' + d.winner.reason + '"</div>';
        h += '<div style="text-align:center;color:#888;font-size:11px;margin-bottom:12px">Proposed by: <span style="color:#ff9800">' + d.winner.proposed_by + '</span></div>';
        if (d.unanimous) h += '<div style="text-align:center;color:#4caf50;font-size:12px;margin-bottom:12px">🌟 Unanimous decision!</div>';
        h += '<div style="margin-top:12px;padding:8px;background:#0a0a0a;border-radius:4px">';
        h += '<div style="color:#888;font-size:11px;margin-bottom:6px">💡 All Proposals:</div>';
        Object.keys(d.proposals).forEach(function(agent) {
          h += '<div style="font-size:11px;color:#aaa;margin:2px 0;padding:2px 4px">' + d.proposals[agent] + '</div>';
        });
        h += '</div>';
        h += '<div style="margin-top:8px;padding:8px;background:#0a0a0a;border-radius:4px">';
        h += '<div style="color:#888;font-size:11px;margin-bottom:6px">🗳️ Votes:</div>';
        Object.keys(d.votes).forEach(function(voter) {
          h += '<div style="font-size:11px;color:#aaa;margin:2px 0;padding:2px 4px">• ' + voter + ' → <span style="color:#ff9800">' + d.votes[voter] + '</span></div>';
        });
        h += '</div>';
        renderCard('🏛️ Family Naming Ceremony', h);
        return;
      }

      if (d.result) {
        const str = typeof d.result === 'string' ? d.result : JSON.stringify(d.result, null, 2);
        log(str, 'ok');
        return;
      }

      if (d.error) {
        log(d.error, 'err');
        return;
      }

      const raw = JSON.stringify(d, null, 2);
      if (raw.length > 50) {
        renderCard('📋 Response', '<pre class="pre-wrap">' + raw.replace(/</g,'&lt;') + '</pre>');
      } else {
        log(raw, 'ok');
      }
    }

    function chatMember(name) {
      const msg = prompt('Message to ' + name + ':');
      if (msg) send({command:'family_chat', member:name, message:msg});
    }

    function solveUI() {
      const p = prompt('Problem to solve:');
      if (p) send({command:'family_solve', problem:p});
    }

    function codeUI() {
      const r = prompt('What code do you need? (e.g. "quick sort"):');
      if (r) send({command:'family_code', request:r});
    }

    function geniusUI() {
      const p = prompt('Ask the family genius:');
      if (p) send({command:'family_genius', prompt:p});
    }

    function mintCoinUI() {
      const a = prompt('Agent name (e.g. Red, Scout, Nexus):');
      if (a) send({command:'family_coin', action:'mint', agent:a});
    }

    function addLiqUI() {
      const a = prompt('Agent name:');
      if (!a) return;
      const amt = prompt('Amount $:');
      if (amt) send({command:'family_coin', action:'liquidity', agent:a, amount:parseFloat(amt)});
    }

    function gainLiqUI() {
      const a = prompt('Agent name:');
      if (a) send({command:'family_coin', action:'gain', agent:a});
    }

    function pipelineUI() {
      const t = prompt('Pipeline type: content, trading, freelance, games, affiliate, code, triple');
      if (t) send({command:'family_income', action:'pipeline', type:t});
    }

    function airdropTaskUI() {
      const p = prompt('Airdrop project name (e.g. LayerZero, zkSync):', 'LayerZero');
      if (p) send({command:'family_airdrop_tasks', project:p, url:''});
    }

    function walletUI() {
      const w = prompt('Your wallet address (0x...):');
      if (w) send({command:'family_airdrop', action:'wallet', address:w});
    }

    function searchUI() {
      const q = prompt('Search the web:');
      if (q) send({command:'family_search', query:q});
    }

    function affiliateUI() {
      const n = prompt('Niche (crypto, fitness, tech, business):', 'crypto');
      if (n) send({command:'family_affiliate', niche:n});
    }

    function adoptUI() {
      const n = prompt('Name to adopt:');
      if (!n) return;
      const r = prompt('Role:');
      send({command:'family_adopt', name:n, role:r || 'adopted'});
    }

    function tokenUI() {
      const name = prompt('Token name:');
      if (name) {
        const sym = prompt('Symbol (optional):');
        send({command:'mint_token', name:name, symbol:sym || ''});
      }
    }

    function tradeUI() {
      const sym = prompt('Symbol (e.g. XBTZAR, BTCUSDT):', 'XBTZAR');
      if (!sym) return;
      const side = prompt('Side (BUY/SELL):', 'BUY');
      if (!side) return;
      const amt = prompt('Amount:', '10');
      if (!amt) return;
      send({command:'trade', symbol:sym, side:side, amount:parseFloat(amt)});
    }

    function doSend() {
      const inp = document.getElementById('input');
      const val = inp.value.trim();
      if (!val) return;
      inp.value = '';

      try { const payload = JSON.parse(val); send(payload); return; } catch(e) {}

      const lower = val.toLowerCase().trim();
      const cmdMap = {
        'status': {command:'status'},
        's': {command:'status'},
        'weekly': {command:'weekly'},
        'w': {command:'weekly'},
        'milestone': {command:'milestone_check'},
        'tokens': {command:'tokens_list'},
        'treasury': {command:'treasury_report'},
        'liquid': {command:'liquidity_report'},
        'tournament': {command:'tournament_round'},
        'lb': {command:'tournament_leaderboard'},
        'leaderboard': {command:'tournament_leaderboard'},
        'deploy': {command:'deploy'},
        'games': {command:'forge', count:3},
        'balance': {command:'balance'},
        'bal': {command:'balance'},
        'notifications': {command:'notifications'},
        'notif': {command:'notifications'},
        'log': {command:'log'},
        'route': {command:'route_revenue', source:'Manual', amount:100},
        'scan': {command:'scan_all', category:'all'},
        'help': {command:'status'}
      };

      if (cmdMap[lower]) { send(cmdMap[lower]); return; }

      if (lower.startsWith('chat ')) {
        const parts = val.split(' ');
        const member = parts[1];
        const msg = parts.slice(2).join(' ') || 'hello';
        send({command:'chat', member:member, message:msg});
        return;
      }

      if (lower.startsWith('search ') || lower.startsWith('find ')) {
        const query = val.split(' ').slice(1).join(' ');
        send({command:'search', query:query});
        return;
      }

      send({command:'search', query:val});
    }

    document.getElementById('input').addEventListener('keydown', e => { if (e.key === 'Enter') doSend(); });
    window.addEventListener('load', () => {
      // Auto-run family startup sequence
      log('🚀 Red Engine V2 starting up...', 'ok');
      setTimeout(() => send({command:'family_overseer'}), 500);
      setTimeout(() => send({command:'family_income', action:'scan'}), 1500);
      setTimeout(() => {
        send({command:'family_income', action:'pipeline', type:'content'});
        send({command:'family_income', action:'pipeline', type:'freelance'});
        send({command:'family_income', action:'pipeline', type:'code'});
        send({command:'family_income', action:'pipeline', type:'affiliate'});
        send({command:'family_income', action:'pipeline', type:'games'});
      }, 3000);
      setTimeout(() => send({command:'family_word'}), 5000);
      setTimeout(() => send({command:'family_coin', action:'report'}), 6500);
      setTimeout(() => log('✅ Family fully operational. Ready for commands.', 'ok'), 8000);
    });
  </script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html", "/web"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(PAGE.encode())
        elif self.path.startswith("/builds/"):
            self._serve_static()
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_static(self):
        """Serve generated game files."""
        base = Path(__file__).parent.parent / "builds"
        rel = self.path.lstrip("/")
        full_path = base / rel
        if full_path.exists() and full_path.is_file():
            self.send_response(200)
            if str(full_path).endswith(".html"):
                self.send_header("Content-Type", "text/html; charset=utf-8")
            elif str(full_path).endswith(".json"):
                self.send_header("Content-Type", "application/json")
            elif str(full_path).endswith(".png"):
                self.send_header("Content-Type", "image/png")
            else:
                self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            with open(full_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api":
            cl = self.headers.get("Content-Length")
            if not cl:
                self._respond({"error": "Missing Content-Length"})
                return
            body = self.rfile.read(int(cl))
            try:
                payload = json.loads(body)
                result = self._execute_command(payload)
                self._respond(result)
            except json.JSONDecodeError:
                self._respond({"error": "Invalid JSON"})
            except subprocess.TimeoutExpired:
                self._respond({"error": "Command timed out"})
            except Exception as e:
                self._respond({"error": str(e)})
        else:
            self._respond({"error": "Not found"}, 404)

    def _execute_command(self, payload):
        cmd = payload.get("command", "")
        env = os.environ.copy()
        home = env.get("HOME", "/home/j")
        env["PATH"] = f"{home}/.local/bin:{env.get('PATH', '')}"

        # Map every command to CLI arguments
        direct_map = {
            "status": ["status"],
            "weekly": ["weekly"],
            "milestone_check": ["milestone_check"],
            "reskin": ["reskin"],
            "deploy": ["deploy"],
            "tokens_list": ["tokens_list"],
            "treasury_report": ["treasury_report"],
            "liquidity_report": ["liquidity_report"],
            "tournament_round": ["tournament"],
            "tournament_leaderboard": ["tournament_leaderboard"],
            "tournament_stop": ["tournament_stop"],
            "notifications": ["notifications"],
            "log": ["log"],
            "media_test": ["media_test"],
            "media_stats": ["media_stats"],
        }

        if cmd in direct_map:
            args = direct_map[cmd]
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT] + args,
                capture_output=True, timeout=60, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out}
            return {"result": "Command executed"}

        if cmd == "forge":
            count = str(payload.get("count", 1))
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "forge", count],
                capture_output=True, timeout=30, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out}
            return {"error": "No output from forge"}

        if cmd in ("mint", "mint_token"):
            name = payload.get("name", "Red Coin")
            symbol = payload.get("symbol", "")
            args = ["mint", name]
            if symbol:
                args.append(symbol)
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT] + args,
                capture_output=True, timeout=15, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out}
            return {"error": "No output"}

        if cmd == "chat":
            member = payload.get("member", "Red")
            message = payload.get("message", "hello")
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "chat", member, message],
                capture_output=True, timeout=15, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"member": member, "reply": out[:500]}
            return {"member": member, "reply": "..."}

        if cmd == "search":
            query = payload.get("query", "")
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "search", query],
                capture_output=True, timeout=30, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"result": f"Searched: {query}"}

        if cmd == "scan_all":
            cat = payload.get("category", "all")
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "scan_all", cat],
                capture_output=True, timeout=30, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"error": "No output"}

        if cmd == "science":
            topic = payload.get("topic", "general")
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "science", topic],
                capture_output=True, timeout=30, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"error": "No output"}

        if cmd == "balance":
            ex = payload.get("exchange", "luno")
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "balance", ex],
                capture_output=True, timeout=15, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"error": "No output"}

        if cmd == "trade":
            symbol = payload.get("symbol", "XBTZAR")
            side = payload.get("side", "BUY")
            amount = str(payload.get("amount", 10))
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "trade", "luno", symbol, side, amount],
                capture_output=True, timeout=20, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"error": "No output"}

        if cmd == "route_revenue":
            src = payload.get("source", "Web UI")
            amt = str(payload.get("amount", 100))
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "route_revenue", src, amt],
                capture_output=True, timeout=15, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"error": "No output"}

        if cmd == "tournament_start":
            interval = str(payload.get("interval", 300))
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "tournament_start", interval],
                capture_output=True, timeout=10, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out}
            return {"result": "Tournament started"}

        if cmd == "jobs":
            cat = payload.get("category", "all")
            result = subprocess.run(
                [sys.executable, ENGINE_SCRIPT, "jobs", cat],
                capture_output=True, timeout=30, env=env
            )
            out = result.stdout.decode().strip()
            if out:
                try:
                    return json.loads(out.split("\n")[-1])
                except (json.JSONDecodeError, IndexError):
                    return {"result": out[:500]}
            return {"error": "No output"}

        # === Family Commands (direct import) ===
        return self._family_command(cmd, payload)

    def _family(self):
        if not hasattr(self, '_family_instance'):
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from agents.family import AgentFamily
            from agents.income import IncomePipeline
            class MockEngine:
                class config:
                    @staticmethod
                    def get(key, default=None):
                        if key == 'family.members':
                            return [
                                {'name': 'Red', 'role': 'Coordinator', 'emoji': '🔴', 'color': '#ff3333', 'purpose': 'lead', 'autonomy': True},
                                {'name': 'Scout', 'role': 'Web Scout', 'emoji': '🔍', 'color': '#00ff88', 'autonomy': True},
                                {'name': 'Forge', 'role': 'Game Builder', 'emoji': '⚒️', 'color': '#ff8800', 'autonomy': True},
                                {'name': 'Quill', 'role': 'Content Creator', 'emoji': '📝', 'color': '#8800ff', 'autonomy': True},
                                {'name': 'Aura', 'role': 'Visual Artist', 'emoji': '🎨', 'color': '#ff00aa', 'autonomy': True},
                                {'name': 'Pane', 'role': 'Dashboard', 'emoji': '📊', 'color': '#00aaff', 'autonomy': True},
                                {'name': 'Nexus', 'role': 'Trader', 'emoji': '🧮', 'color': '#ffff00', 'autonomy': True},
                                {'name': 'Psyche', 'role': 'Pattern Analyst', 'emoji': '🧠', 'color': '#aa00ff', 'autonomy': True, 'personality': 'wise'},
                                {'name': 'Lucid', 'role': 'Knowledge', 'emoji': '🔮', 'color': '#00ffaa', 'autonomy': True},
                                {'name': 'Jobs', 'role': 'Income Creator', 'emoji': '💼', 'color': '#ff8844', 'autonomy': True},
                                {'name': 'Codex', 'role': 'Code Builder', 'emoji': '💻', 'color': '#88ff00', 'autonomy': True},
                            ]
                        return default
                def log(self, msg):
                    pass
            e = MockEngine()
            self._family_instance = AgentFamily(e)
            self._pipeline = IncomePipeline(e, self._family_instance)
            self._family_instance.set_autonomy('All', True)
        return self._family_instance, self._pipeline

    def _family_command(self, cmd, payload):
        family, pipeline = self._family()
        try:
            if cmd == "family_chat":
                member = payload.get("member", "Red")
                msg = payload.get("message", "hello")
                return family.chat(member, msg)

            if cmd == "family_ask":
                q = payload.get("question", "")
                return family.ask(q)

            if cmd == "family_overseer":
                return family.overseer()

            if cmd == "family_naming":
                return family.family_naming_ceremony()

            if cmd == "family_solve":
                p = payload.get("problem", "")
                return family.solve(p)

            if cmd == "family_code":
                r = payload.get("request", "")
                return family.code(r)

            if cmd == "family_genius":
                p = payload.get("prompt", "")
                return family.genius(p)

            if cmd == "family_income":
                action = payload.get("action", "report")
                if action == "report":
                    return pipeline.report()
                if action == "scan":
                    return pipeline.scan_opportunities()
                if action == "execute":
                    return pipeline.execute_all()
                if action == "pipeline":
                    ptype = payload.get("type", "content")
                    return pipeline.activate_pipeline(ptype)
                if action == "route":
                    amt = payload.get("amount", 0)
                    return pipeline.route_funds(amt)
                return {"error": f"Unknown income action: {action}"}

            if cmd == "family_coin":
                action = payload.get("action", "report")
                if action == "mint":
                    agent = payload.get("agent", "")
                    return pipeline.mint_agent_coin(agent)
                if action == "liquidity":
                    agent = payload.get("agent", "")
                    amt = payload.get("amount", 0)
                    return pipeline.add_liquidity(agent, amt)
                if action == "gain":
                    agent = payload.get("agent", "")
                    return pipeline.gain_liquidity(agent)
                if action == "report":
                    return pipeline.coin_report()
                return {"error": f"Unknown coin action: {action}"}

            if cmd == "family_airdrop":
                action = payload.get("action", "scan")
                if action == "scan":
                    wallet = payload.get("wallet", "")
                    return family.airdrop_scanner(wallet)
                if action == "live":
                    return family.airdrops_live()
                if action == "wallet":
                    addr = payload.get("address", "")
                    return family.set_airdrop_wallet(addr)
                if action == "check":
                    return family.check_airdrop_wallet()
                return {"error": f"Unknown airdrop action: {action}"}

            if cmd == "family_airdrop_tasks":
                project = payload.get("project", "")
                url = payload.get("url", "")
                return family.airdrop_task_generator(project, url)

            if cmd == "family_search":
                query = payload.get("query", "")
                return family.search_web(query)

            if cmd == "family_affiliate":
                niche = payload.get("niche", "business")
                return family.affiliate_generator(niche=niche)

            if cmd == "family_sync":
                folder = payload.get("folder", "/mnt/gdrive/RedEngine")
                return family.sync_simple(folder)

            if cmd == "family_word":
                return family.word_of_the_day()

            if cmd == "family_evolve":
                return family.evolve()

            if cmd == "family_recalibrate":
                return family.recalibrate()

            if cmd == "family_upgrade":
                utype = payload.get("type", "standard")
                return family.upgrade(utype)

            if cmd == "family_protect":
                enable = payload.get("enable", True)
                return family.protect(enable)

            if cmd == "family_profit":
                target = payload.get("target", "")
                amt = payload.get("amount", 0)
                return family.profit_target(target, amt)

            if cmd == "family_cluster":
                action = payload.get("action", "discover")
                if action == "discover":
                    return family.discover_cluster()
                if action == "reproduce":
                    cid = payload.get("cluster_id", 1)
                    return family.reproduce(cid)
                if action == "list":
                    return {"clusters": family.get_clusters()}
                return {"error": f"Unknown cluster action: {action}"}

            if cmd == "family_adopt":
                name = payload.get("name", "")
                role = payload.get("role", "adopted")
                return family.adopt(name, role)

            if cmd == "family_fraud":
                msg = payload.get("message", "")
                fraud = family.detect_fraud(msg)
                if fraud:
                    return {"fraud": True, "details": fraud}
                return {"fraud": False, "message": "Looks normal"}

        except Exception as e:
            return {"error": f"Family command error: {str(e)}"}

        return {"error": f"Unknown family command: {cmd}"}

    def _respond(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"Red Engine V2 Web UI → http://localhost:{port}")
    HTTPServer(("", port), Handler).serve_forever()
