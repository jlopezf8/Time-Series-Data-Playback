# Time Series Data Playback

A Python-based tool for replaying time series data acquisitions.

## Prerequisites

- Python 3.8 or higher

## Installation

1. Clone the repository:  
   ```bash
git clone https://github.com/jlopezf8/time-series-data-playback.git
   ```
2. Change into the project directory:  
   ```bash
cd time-series-data-playback
   ```
3. (Optional) Create and activate a virtual environment:  
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

## Usage

- On Windows, run the batch wrapper:  
  ```bash
  run_replay_generator.bat
  ```
- Or invoke the Python script directly:  
  ```bash
  python create_replay.py [options]
  ```

## Project Structure

- **create_replay.py**  
  Core Python script that generates replay data.
- **run_replay_generator.bat**  
  Windows batch file for launching the replay generator.
- **Instrucciones.pdf**  
  Detailed instructions and usage guide (in Spanish).

## Contributing

Contributions, issues, and feature requests are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
