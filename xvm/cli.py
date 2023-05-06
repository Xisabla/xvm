import subprocess
import typer

# Quick, dirty and very not complete implementation of a CLI for VirtualBox
# Simply allows to start, stop and list VMs

# Maybe one day I'll make this a proper version of this tool
# Some improvements that I could use:
# - Add a config file to store the path to VBoxManage and other options
# - Have dedicated classes for VMs and VM lists (dataclasses would be perfect)
# - Allow better filtering of VMs (e.g. by state, name, etc.)
# - Customize the output of the list command (with a --format option)
# - Add disks management for VMs (create, attach, detach, list, etc.)
# - Add network management for VMs (create, attach, detach, list, etc.)
# - Add a command to create a VM from a template
# - Add a command to clone a VM

app = typer.Typer()

VBOX_MANAGE = "/mnt/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"

VM_LIST_FIELDS = [
    "Name",
    "Guest OS",
    "Memory size",
    "Number of CPUs",
    "State",
]

"""Executes a VBoxManage command and returns the output
"""
def vbox_manage(*args):
    # Execute the VBoxManage command
    try:
        proc = subprocess.run([VBOX_MANAGE, *args], capture_output=True)
    except FileNotFoundError:
        typer.echo(f"Could not find VirtualBox executable at {VBOX_MANAGE}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"An error occured while executing VirtualBox: {e}")
        raise typer.Exit(code=1) 

    # Check if the command was successful
    if proc.returncode != 0:
        typer.echo(proc.stderr.decode("utf-8"))
        raise typer.Exit(code=proc.returncode)

    # Return the output
    return proc.stdout.decode("utf-8")

"""Lists all virtualbox VMs
"""
def vbox_vms_list(sorted=True, long=False):
    args = [ "list", "vms" ]

    # Add the arguments
    if long: args.append("-l")
    if sorted: args.append("-s")

    output = vbox_manage(*args)

    if long:
        vms = []

        for line in output.splitlines():
            if line.startswith("Name:"):
                vms.append({ "Name": line.split(":")[1].strip() })
            elif len(vms) > 0:
                field = line.split(":")[0]

                if field in VM_LIST_FIELDS:
                    vms[-1][field] = line.split(":")[1].strip()

        return [
            f'{vm["Name"]} ({vm["Guest OS"]}): {vm["State"].split(" ")[0]} - {vm["Memory size"]}MB RAM, {vm["Number of CPUs"]} CPUs'
            for vm in vms
            ]
    else:
        vms = [ line.split(" ")[0].strip('"') for line in output.splitlines() ]
        
        return vms

# Start a virtualbox VM
@app.command()
def start(name: str, headless: bool = False):
    # Check if the VM exists
    if name not in vbox_vms_list(sorted=False, long=False):
        typer.echo(f"VM {name} does not exist")
        raise typer.Exit(code=1)

    # Check if the VM is already running using VBoxManage
    if "running" in vbox_manage("showvminfo", name):
        typer.echo(f"VM {name} is already running")
        raise typer.Exit(code=1)

    # Start the VM in headless mode if requested
    if headless:
        print(f"Starting VM {name} in headless mode...")
        print(vbox_manage("startvm", name, "--type", "headless"))
    else:
        print(f"Starting VM {name}...")
        print(vbox_manage("startvm", name))

# Stop a virtualbox VM
@app.command()
def stop(name: str, force: bool = False):
    # Check if the VM exists
    if name not in vbox_vms_list(sorted=False, long=False):
        typer.echo(f"VM {name} does not exist")
        raise typer.Exit(code=1)

    # Check if the VM is already running using VBoxManage
    if "running" not in vbox_manage("showvminfo", name):
        typer.echo(f"VM {name} is not running")
        raise typer.Exit(code=1)

    # Force stop the VM if requested
    if force:
        print(f"Forcing VM {name} to stop...")
        print(vbox_manage("controlvm", name, "poweroff"))
    else:
        print(f"Stopping VM {name}...")
        print(vbox_manage("controlvm", name, "acpipowerbutton"))

# Stop all virtualbox VMs
@app.command()
def stop_all(force: bool = False):
    # Get all running VMs
    vms = vbox_vms_list(sorted=False, long=False)

    # Stop each VM
    for vm in vms:
        if "running" in vbox_manage("showvminfo", vm):
            stop(vm, force=force)

# List all virtualbox VMs
@app.command()
def list(sorted: bool = True, details: bool = True):
    vms = vbox_vms_list(sorted=sorted, long=details)

    # Print the VMs
    print('\n'.join([ str(vm) for vm in vms]))

if __name__ == "__main__":
    app()
