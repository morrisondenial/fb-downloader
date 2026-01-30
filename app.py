from flask import Flask, render_template_string, request, jsonify, Response
import yt_dlp
import requests

app = Flask(__name__)

# --- HTML/CSS/JS DESIGN ---
UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 flex items-center justify-center p-4 min-h-screen">
    <div class="max-w-md w-full bg-white rounded-3xl shadow-xl p-6 border border-gray-100">
        <h2 class="text-xl font-black text-blue-600 mb-4 text-center">FB DOWNLOADER</h2>
        <input type="text" id="url" placeholder="Paste link here..." class="w-full p-4 bg-gray-100 rounded-xl mb-3 outline-none focus:ring-2 focus:ring-blue-400">
        <button onclick="fetchVid()" id="btn" class="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg active:scale-95 transition">GET VIDEO</button>

        <div id="loader" class="hidden text-center py-6 animate-pulse text-gray-400">Searching Facebook...</div>

        <div id="res" class="hidden mt-6 animate-in fade-in duration-500">
            <video id="preview" controls class="w-full rounded-xl bg-black mb-4 aspect-video shadow-md"></video>
            <div class="grid grid-cols-2 gap-2 mb-4">
                <button onclick="dl('hd')" class="bg-green-500 text-white py-3 rounded-lg font-bold">Download HD</button>
                <button onclick="dl('sd')" class="bg-blue-500 text-white py-3 rounded-lg font-bold">Download SD</button>
            </div>
            <div class="border-t pt-4">
                <p class="text-[10px] font-bold text-gray-400 uppercase mb-2">Other Options</p>
                <div class="flex gap-2">
                    <button onclick="dl('low')" class="flex-1 bg-gray-100 py-2 rounded text-xs font-bold text-gray-500">LOW QUAL</button>
                    <button onclick="dl('hd')" class="flex-1 bg-gray-100 py-2 rounded text-xs font-bold text-gray-500">FORCE HD</button>
                    <button onclick="dl('sd')" class="flex-1 bg-gray-100 py-2 rounded text-xs font-bold text-gray-500">FORCE SD</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        let links = {};
        async function fetchVid() {
            const u = document.getElementById('url').value;
            if(!u) return;
            document.getElementById('loader').classList.remove('hidden');
            document.getElementById('res').classList.add('hidden');
            const r = await fetch('/get', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url:u})});
            const d = await r.json();
            document.getElementById('loader').classList.add('hidden');
            if(d.ok) {
                links = d.links;
                document.getElementById('preview').src = d.preview;
                document.getElementById('res').classList.remove('hidden');
            } else { alert("Video not found!"); }
        }
        function dl(t) { window.location.href = `/save?url=${encodeURIComponent(links[t])}&name=${t}`; }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---
@app.route('/')
def home(): return render_template_string(UI)

@app.route('/get', methods=['POST'])
def get():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            f = info.get('formats', [])
            hd = next((x['url'] for x in f if x.get('height') and x.get('height') >= 720), None)
            sd = next((x['url'] for x in f if x.get('height') and 360 <= x.get('height') < 720), None)
            low = next((x['url'] for x in f if x.get('height') and x.get('height') < 360), sd)
            return jsonify({'ok': True, 'preview': sd or hd, 'links': {'hd': hd or sd, 'sd': sd or low, 'low': low}})
    except: return jsonify({'ok': False})

@app.route('/save')
def save():
    v_url = request.args.get('url')
    r = requests.get(v_url, stream=True)
    return Response(r.iter_content(chunk_size=1024), headers={"Content-Disposition": f"attachment; filename=video.mp4"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)