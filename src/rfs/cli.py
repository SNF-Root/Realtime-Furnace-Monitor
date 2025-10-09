import click
from rfs.main import run_main
from rfs.main import arucocap
from rfs.setup.calServer import run_calServer
from rfs.main import capturefirst1080p
import time
import cv2
from pathlib import Path
import json
from rfs.context import calContext



BASE_DIR = Path(__file__).parents[1].resolve()
ARUCO_COORD_FILE = BASE_DIR / "setup" / "aruco_coord.json"



logo = """
                                                             
                                                             
RRRRRRRRRRRRRRRRR   FFFFFFFFFFFFFFFFFFFFFF   SSSSSSSSSSSSSSS 
R::::::::::::::::R  F::::::::::::::::::::F SS:::::::::::::::S
R::::::RRRRRR:::::R F::::::::::::::::::::FS:::::SSSSSS::::::S
RR:::::R     R:::::RFF::::::FFFFFFFFF::::FS:::::S     SSSSSSS
  R::::R     R:::::R  F:::::F       FFFFFFS:::::S            
  R::::R     R:::::R  F:::::F             S:::::S            
  R::::RRRRRR:::::R   F::::::FFFFFFFFFF    S::::SSSS         
  R:::::::::::::RR    F:::::::::::::::F     SS::::::SSSSS    
  R::::RRRRRR:::::R   F:::::::::::::::F       SSS::::::::SS  
  R::::R     R:::::R  F::::::FFFFFFFFFF          SSSSSS::::S 
  R::::R     R:::::R  F:::::F                         S:::::S
  R::::R     R:::::R  F:::::F                         S:::::S
RR:::::R     R:::::RFF:::::::FF           SSSSSSS     S:::::S
R::::::R     R:::::RF::::::::FF           S::::::SSSSSS:::::S
R::::::R     R:::::RF::::::::FF           S:::::::::::::::SS 
RRRRRRRR     RRRRRRRFFFFFFFFFFF            SSSSSSSSSSSSSSS   
                                                             
                                                             
                                                             
                                                             
                                                                                                                
                                                             
"""




def write_aruco_status(status: int):
    try:
        with open(ARUCO_COORD_FILE, "w") as f:
            json.dump([{"status": status}], f, indent = 2)
            print("wrote status succesfully")

    except Exception as e:
        print(e)

def read_data():
    if ARUCO_COORD_FILE.exists():
        with open(ARUCO_COORD_FILE, 'r') as f:
            return json.load(f)
    else:
        return []
    

# def add_aruco_coords(aruco_coord):
#     try:
#         existing_data = read_data()
#         existing_data.append(aruco_coord)
#         with open(ARUCO_COORD_FILE, "w") as f:
#             json.dump()



@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--calibrate", is_flag=True, help="Start calibration web server.")
@click.option("--run", "run_flag", is_flag=True, help="Run the tool.")
def cli(calibrate: bool, run_flag: bool):
    """RFS CLI – minimal two-flag launcher."""

    print(logo)

    if calibrate and run_flag:
        raise click.UsageError("Choose exactly one: --calibrate OR --run")
    if not calibrate and not run_flag:
        raise click.UsageError("You must pass one of: --calibrate or --run")

    # Dispatch
    if calibrate:

        ctx = calContext()

        keep = False
        while(not keep):
            capturefirst1080p("pictureTaken.jpg")
            keep = click.prompt("y to accept or n to reject image")
            if keep == 'y' or keep == 'Y':
                keep = True
            elif keep == 'n' or keep == 'N':
                keep = False
                click.secho("retrying...", fg='yellow')
                continue
            else:
                keep = False
                click.secho("invalid entry", fg = "red", bold = True)
                click.secho("retrying...", fg = "yellow")
                continue
            
            id_position = arucocap("images/highres (1).jpg")
            if(len(id_position) == 0):
                keep = False
                click.secho("no aruco codes detected", fg = "red", bold=True)
                click.echo("retrying...")
        click.secho(str(id_position), fg = "green", bold=True)

        ctx.set_id(id_position)


        click.secho("setting up server...", fg = "yellow") 
        return run_calServer(ctx)
    else:
        #do the aruco subtraction and then write to the aruco coords json file

        return run_main()


if __name__ == "__main__":
    cli()