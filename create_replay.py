import pandas as pd
import numpy as np
import json
import os
import sys # Import the sys module to read command-line arguments

def create_replay_app_from_file(file_path):
    """
    Loads time-series data from a local CSV, resamples it, and generates
    a self-contained HTML file for a dynamic replay.
    """
    # --- 1. Load and Prepare Data from the local file path ---
    try:
        file_name = os.path.basename(file_path)

        # Read the CSV file, parsing the first column as dates.
        df = pd.read_csv(file_path, parse_dates=[0])
        df = df.set_index('Time')
        df.sort_index(inplace=True)
        print(f"✅ Raw data loaded successfully from '{file_name}'.")
        print(f"   Loaded {len(df)} raw data points.")

        # --- Resample the data to a 1-second frequency ---
        df_resampled = df.resample('s').mean()
        df_resampled.dropna(inplace=True)
        
        print(f"✅ Data resampled to 1-second frequency ({len(df_resampled)} points).")

    except FileNotFoundError:
        print(f"❌ ERROR: The file was not found at '{file_path}'.")
        return None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

    # Convert the DataFrame to a JSON format.
    data_json = df_resampled.to_json(orient='split', date_format='iso')

    # --- 2. Define the HTML and JavaScript for the Application ---
    # This part is identical to the previous version
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Time-Series Replay</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; }}
        .control-panel button {{ transition: all 0.2s ease-in-out; }}
        .control-panel button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .value-card {{ transition: all 0.2s ease-in-out; border-left-width: 4px; }}
    </style>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto bg-white rounded-xl shadow-lg p-4 md:p-6">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-800">Dynamic Time-Series Replay</h1>
        <p class="text-sm text-gray-500 mt-1">Source File: {file_name}</p>
        <p class="text-gray-500 my-6"><b>Click on the chart</b> to set a starting point, then use the controls to play, pause, and change the replay speed.</p>
        <div id="chart" class="w-full h-[600px]"></div>
        <div id="value-display" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mt-6"></div>
        <div class="control-panel mt-6 p-4 bg-gray-50 rounded-lg flex flex-wrap items-center justify-center gap-4">
            <button id="reset-btn" class="px-5 py-2.5 bg-gray-500 text-white font-semibold rounded-lg shadow-md">Reset</button>
            <button id="play-pause-btn" class="px-5 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md w-32">Play</button>
            <div class="flex items-center gap-2">
                <label for="speed-select" class="font-medium text-gray-700">Speed:</label>
                <select id="speed-select" class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5">
                    <option value="1000">1x (1 Data/Min)</option>
                    <option value="200">5x</option>
                    <option value="100">10x</option>
                    <option value="20" selected>50x</option>
                    <option value="10">100x</option>
                </select>
            </div>
        </div>
    </div>
    <script>
        const data = {json.loads(data_json)};
        const timestamps = data.index.map(t => new Date(t));
        let currentIndex = 0, isPlaying = false, intervalId = null;
        const chartDiv = document.getElementById('chart'), playPauseBtn = document.getElementById('play-pause-btn'), resetBtn = document.getElementById('reset-btn'), speedSelect = document.getElementById('speed-select'), valueDisplay = document.getElementById('value-display');
        const colors = ['#3b82f6', '#10b981', '#ef4444', '#f97316', '#8b5cf6', '#d946ef'];
        function initializePlot() {{
            const traces = data.columns.map((col, i) => ({{ x: timestamps, y: data.data.map(row => row[i]), type: 'scattergl', mode: 'lines', name: col, line: {{ color: colors[i % colors.length] }} }}));
            const layout = {{ title: 'Sensor Readings Over Time', xaxis: {{ title: 'Time', rangeslider: {{ visible: true }} }}, yaxis: {{ title: 'Value', fixedrange: true }}, hovermode: 'x unified', showlegend: true, legend: {{ x: 0, y: 1.1, orientation: 'h' }}, shapes: [{{ type: 'line', x0: timestamps[0], y0: 0, x1: timestamps[0], y1: 1, yref: 'paper', line: {{ color: 'rgba(0,0,0,0.5)', width: 2, dash: 'dash' }} }}] }};
            Plotly.newPlot(chartDiv, traces, layout, {{ responsive: true }});
            createValueCards();
            updateValueDisplay();
            chartDiv.on('plotly_click', function(eventData) {{
                if (isPlaying) pauseReplay();
                const closestIndex = findClosestTimestampIndex(new Date(eventData.points[0].x));
                if (closestIndex !== -1) {{ currentIndex = closestIndex; updateReplayPosition(); }}
            }});
        }}
        function createValueCards() {{ valueDisplay.innerHTML = ''; data.columns.forEach((col, i) => {{ const card = document.createElement('div'); card.className = 'value-card bg-white rounded-lg p-4 shadow border-l-4'; card.style.borderColor = colors[i % colors.length]; card.innerHTML = `<p class="text-sm font-medium text-gray-500 truncate" title="${{col}}">${{col}}</p><p id="value-${{i}}" class="text-2xl font-bold text-gray-800 mt-1">0.00</p>`; valueDisplay.appendChild(card); }}); }}
        function findClosestTimestampIndex(targetDate) {{ if (!timestamps || timestamps.length === 0) return -1; let closestIndex = 0, minDiff = Math.abs(targetDate - timestamps[0]); for (let i = 1; i < timestamps.length; i++) {{ const diff = Math.abs(targetDate - timestamps[i]); if (diff < minDiff) {{ minDiff = diff; closestIndex = i; }} }} return closestIndex; }}
        function updateReplayPosition() {{ const newLayout = {{ 'shapes[0].x0': timestamps[currentIndex], 'shapes[0].x1': timestamps[currentIndex] }}; Plotly.relayout(chartDiv, newLayout); updateValueDisplay(); }}
        function updateValueDisplay() {{ if (currentIndex >= data.data.length) return; data.columns.forEach((col, i) => {{ const value = data.data[currentIndex][i]; const element = document.getElementById(`value-${{i}}`); if(element) element.textContent = value.toFixed(2); }}); }}
        function advanceFrame() {{ currentIndex++; if (currentIndex >= timestamps.length) {{ pauseReplay(); currentIndex = timestamps.length - 1; return; }} updateReplayPosition(); }}
        function playReplay() {{ if (isPlaying) return; isPlaying = true; playPauseBtn.textContent = 'Pause'; playPauseBtn.classList.replace('bg-blue-600', 'bg-orange-500'); if (currentIndex >= timestamps.length - 1) currentIndex = 0; const intervalMilliseconds = parseInt(speedSelect.value, 10); clearInterval(intervalId); intervalId = setInterval(advanceFrame, intervalMilliseconds); }}
        function pauseReplay() {{ isPlaying = false; playPauseBtn.textContent = 'Play'; playPauseBtn.classList.replace('bg-orange-500', 'bg-blue-600'); clearInterval(intervalId); }}
        function resetReplay() {{ pauseReplay(); currentIndex = 0; updateReplayPosition(); }}
        playPauseBtn.addEventListener('click', () => isPlaying ? pauseReplay() : playReplay());
        resetBtn.addEventListener('click', resetReplay);
        speedSelect.addEventListener('change', () => {{ if (isPlaying) playReplay(); }});
        document.addEventListener('DOMContentLoaded', initializePlot);
    </script>
</body>
</html>
    """
    return html_template, file_name

# --- Main execution block ---
if __name__ == '__main__':
    # Check if a file path was provided as a command-line argument
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        print("❌ ERROR: Please provide a CSV file path to process.")
        print("Usage: python create_replay.py \"path/to/your/file.csv\"")
        sys.exit(1) # Exit the script if no file is provided

    # Generate the HTML content
    app_html, source_file_name = create_replay_app_from_file(input_file_path)
    
    # If HTML was created, save it to a file
    if app_html:
        # Create a clean output filename based on the source file
        base_name = os.path.splitext(source_file_name)[0]
        output_filename = f"replay_for_{base_name}.html"
        
        with open(output_filename, "w", encoding='utf-8') as f:
            f.write(app_html)
            
        print(f"\n✅ Successfully created '{output_filename}'.")
        print("   You can now open this file in your web browser.")

