import os
import sys
import subprocess
import pandas as pd

python_executable = sys.executable
SOLARNET_REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'SolarNet_plus'))
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ai_models', 'best_model.pth')
IMAGE_FOLDER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'test_data'))
IMAGE_FILE_PATH = os.path.join(IMAGE_FOLDER_PATH, 'ait_pune_campus.png')

def analyze_ait_campus():
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        if not os.path.exists(IMAGE_FILE_PATH):
            raise FileNotFoundError(f"Test image not found: {IMAGE_FILE_PATH}")

        # Step A: Prediction
        print("Starting Step A: AI Prediction...")
        orientation_map_dir = os.path.join(SOLARNET_REPO_PATH, 'orientation_output')
        superstructure_map_dir = os.path.join(SOLARNET_REPO_PATH, 'superstructure_output')
        predict_script = os.path.join(SOLARNET_REPO_PATH, 'dlcode', 'predict_patch.py')
        predict_cmd = [
            python_executable, predict_script, '--pretrain_net', MODEL_PATH,
            '--pre_root_dir', IMAGE_FOLDER_PATH, '--preDir2', orientation_map_dir,
            '--preDir3', superstructure_map_dir
        ]
        subprocess.run(predict_cmd, check=True, cwd=SOLARNET_REPO_PATH, capture_output=True, text=True)
        print("Step A Complete.")

        # Step B: PV Calculation
        print("Starting Step B: PV Potential Calculation...")
        output_csv_path = os.path.join(SOLARNET_REPO_PATH, 'pv_results.csv')
        pv_script = os.path.join(SOLARNET_REPO_PATH, 'pvcode', 'cal_pv.py')
        
        # Define the full paths to the generated map files
        orientation_map_file = os.path.join(orientation_map_dir, 'ait_pune_campus.png')
        superstructure_map_file = os.path.join(superstructure_map_dir, 'ait_pune_campus.png')
        
        pv_command = [
            python_executable, pv_script, '--image_path', IMAGE_FILE_PATH,
            '--orientation_path', orientation_map_file, 
            '--superstructure_path', superstructure_map_file,
            '--save_path_csv', output_csv_path
        ]
        subprocess.run(pv_command, check=True, cwd=SOLARNET_REPO_PATH, capture_output=True, text=True)
        print("Step B Complete.")

        # Step C: Read Results
        print("Starting Step C: Formatting results...")
        if not os.path.exists(output_csv_path):
             raise FileNotFoundError(f"Output CSV not found: {output_csv_path}")
        results_df = pd.read_csv(output_csv_path)
        total_potential_kwh = results_df['electricity_generations'].sum()
        
        return {
            "total_potential_gwh_year": round(total_potential_kwh / 1_000_000, 4),
            "potential_by_orientation_kwh": {"Total": round(total_potential_kwh)},
        }

    except subprocess.CalledProcessError as e:
        print(f"Error in external script: {e.stderr}")
        return {"error": "AI script failed. Check backend console."}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}