# capstone
- Course recommender system
- ML web app
- Market analysis

## For Developers:
## Run Application
- Click Terminal
- Click New Terminal
- Enter `streamlit run Streamlit/main.py` in Terminal (it should be runnning on http://localhost:8501)

## Features
`dashboard.py` is the structure of the application and holds most of the core features.
`main.py` is the main file that calls `dashboard.py`.

| Method  | Description |
| ------------- | ------------- |
| app  | Display layout of page and sidebar  |
| trainModel  | use uploaded datasets to train the model and output results  |
| showInputHeader  | Input for user to view course visualizations by course name  |
| showClustersByCourse  | Outputs cluster visualizations by selected demographic  |
| studentDemo  | Outputs cluster visualizations by student  |
| courseDemo  | Outputs cluster visualizations by course  |
| changeCSS  | Manual changes to streamlit css for flexibility  |

## Build Application
This process is used to package the applications together and create an executable file for external users without installing any dependencies on their end.
The executable file can only be used if the user machine has the same operating system as the machine that its built on.

Example: If this application is built on MacOs, it can only be used in machines with the MacOs environment. Same goes to Windows (7/8/10/XP) and Linux.

To create the .exe file:
- Make sure you have all imported pachages installed in your current machine (check all your imports)
- Run `pip install pyinstaller` on your terminal
- Run `pyinstaller --onefile --additional-hooks-dir=./hooks run_main.py --clean` on your terminal (make sure that u are at the root folder aka capstone folder)
- Copy and Paste `Streamlit` folder into `dist` folder
- Double Click run_main in `dist` folder

