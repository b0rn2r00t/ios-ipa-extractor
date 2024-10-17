import paramiko
import os
import sys
import re
import secrets
import string
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, track
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

console = Console()

def generate_random_string(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_ip_and_port(ip_port):
    pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?$'
    match = re.match(pattern, ip_port)
    if not match:
        return None, None
    ip = match.group(1)
    port = int(match.group(2)) if match.group(2) else 22
    if all(0 <= int(n) <= 255 for n in ip.split('.')) and 1 <= port <= 65535:
        return ip, port
    return None, None

def get_ssh_details():
    while True:
        ip_port = Prompt.ask("[bold cyan]Enter iPhone SSH IP and Port[/bold cyan] (default port is 22)")
        ip, port = validate_ip_and_port(ip_port)
        if ip and port:
            break
        rprint("[bold red]Invalid IP or port. Please try again.[/bold red]")
    
    username = Prompt.ask("[bold cyan]Enter iPhone SSH User[/bold cyan]", default="root")
    password = Prompt.ask("[bold cyan]Enter iPhone SSH Password[/bold cyan]", password=True)
    return ip, port, username, password

def ssh_connect(ip, port, username, password):
    try:
        with console.status("[bold green]Connecting to device...", spinner="dots"):
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=port, username=username, password=password, timeout=60)
        rprint(f"[bold green]✅ Connected to {ip}:{port}")
        return client
    except Exception as e:
        rprint(f"[bold red]❌ Connection failed: {str(e)}")
        return None

def run_ssh_command(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        if error:
            rprint(f"[bold red]❌ Error: {error}")
        return output
    except Exception as e:
        rprint(f"[bold red]❌ Command execution failed: {str(e)}")
        return ""

def list_installed_apps(client):
    rprint("[bold yellow]📱 Listing installed applications...")
    command = "ls -d /var/containers/Bundle/Application/*/*.app"
    result = run_ssh_command(client, command)
    
    apps = []
    for line in result.splitlines():
        app_name = line.split('/')[-1].replace('.app', '')
        app_path = line.strip()
        apps.append({
            'name': app_name,
            'path': app_path
        })
    
    return sorted(apps, key=lambda x: x['name'].lower())

def display_app_table(apps):
    table = Table(title="[bold magenta]Installed Applications")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Application Name", style="green")
    table.add_column("Path", style="yellow")

    for i, app in enumerate(apps, 1):
        table.add_row(str(i), app['name'], app['path'])

    console.print(table)

def get_user_selection(apps):
    while True:
        try:
            selection = int(Prompt.ask("[bold cyan]Enter the number of the app to extract[/bold cyan] (or 0 to exit)"))
            if 0 <= selection <= len(apps):
                return selection
            else:
                rprint("[bold red]Invalid selection. Please try again.[/bold red]")
        except ValueError:
            rprint("[bold red]Invalid input. Please enter a number.[/bold red]")

def extract_ipa(client, app_path, ipa_output_name):
    rprint("[bold yellow]📦 Extracting IPA...")
    base_path = os.path.dirname(app_path)
    app_folder_name = os.path.basename(app_path)
    
    temp_dir = f"/tmp/{generate_random_string()}"
    ipa_path = f"{temp_dir}/{ipa_output_name}.ipa"
    
    steps = [
        ("Creating temporary directory", f"mkdir -p {temp_dir}"),
        ("Copying app to temporary directory", f"cp -R {app_path} {temp_dir}/Payload"),
        ("Zipping Payload folder", f"cd {temp_dir} && zip -r {ipa_path} Payload"),
    ]
    
    for step_description, command in track(steps, description="Extracting IPA"):
        run_ssh_command(client, command)
    
    rprint(f"[bold green]✅ IPA created at: {ipa_path}")
    return ipa_path, temp_dir

def get_file_size(client, file_path):
    output = run_ssh_command(client, f"ls -l {file_path}")
    try:
        return int(output.split()[4])
    except (IndexError, ValueError):
        return 0

def download_ipa(client, ip, port, username, password, ipa_path, local_path):
    try:
        transport = paramiko.Transport((ip, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        remote_file_size = get_file_size(client, ipa_path)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Downloading...", justify="right"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[bold cyan]{task.completed}/{task.total}", justify="right"),
        ) as progress:
            task = progress.add_task("Downloading", total=remote_file_size)
            
            def update_progress(transferred, total):
                progress.update(task, completed=transferred)
            
            sftp.get(ipa_path, local_path, callback=update_progress)
        
        rprint(f"[bold green]✅ IPA downloaded to: {local_path}")
        
        sftp.close()
        transport.close()
    except Exception as e:
        rprint(f"[bold red]❌ Download failed: {str(e)}")

def cleanup(client, temp_dir):
    rprint("[bold yellow]🧹 Cleaning up...")
    run_ssh_command(client, f"rm -rf {temp_dir}")
    rprint("[bold green]✅ Cleanup completed")

def get_output_details(app_name):
    default_name = f"{app_name}_extracted.ipa"
    default_path = os.getcwd()
    
    use_default = Prompt.ask(
        f"[bold cyan]Use default output[/bold cyan] (filename: {default_name}, location: {default_path})? (yes/no)",
        default="yes"
    ).lower() == "yes"

    if use_default:
        return os.path.join(default_path, default_name)
    
    filename = Prompt.ask("[bold cyan]Enter the output filename[/bold cyan] (including .ipa extension)", default=default_name)
    location = Prompt.ask("[bold cyan]Enter the output location[/bold cyan]", default=default_path)
    return os.path.join(location, filename)

def main():
    try:
        ip, port, username, password = get_ssh_details()
        ssh_client = ssh_connect(ip, port, username, password)
        
        if ssh_client:
            apps = list_installed_apps(ssh_client)
            if apps:
                display_app_table(apps)
                
                selection = get_user_selection(apps)
                
                if selection == 0:
                    rprint("[bold yellow]Exiting...")
                    return
                
                selected_app = apps[selection - 1]
                ipa_output_name = selected_app['name']
                ipa_remote_path, temp_dir = extract_ipa(ssh_client, selected_app['path'], ipa_output_name)
                local_ipa_path = get_output_details(selected_app['name'])
                download_ipa(ssh_client, ip, port, username, password, ipa_remote_path, local_ipa_path)
                
                cleanup(ssh_client, temp_dir)
            else:
                rprint("[bold red]No applications found or error occurred while listing apps.")
    except Exception as e:
        rprint(f"[bold red]An unexpected error occurred: {str(e)}")
    finally:
        if 'ssh_client' in locals() and ssh_client:
            ssh_client.close()

if __name__ == "__main__":
    main()
