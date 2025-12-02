#!/usr/bin/env pwsh
# Docker Swarm Deployment Script for Biedronka PrestaShop
# Automates cluster initialization and stack deployment

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('deploy', 'update', 'scale', 'stop', 'cleanup', 'status')]
    [string]$Action = 'deploy',
    
    [Parameter(Mandatory=$false)]
    [int]$Replicas = 2
)

$ErrorActionPreference = "Stop"
$StackName = "biedronka"
$ComposeFile = "docker/docker-compose-prod.yml"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Initialize-Swarm {
    Write-Step "Checking Docker Swarm status..."
    
    $swarmStatus = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
    
    if ($swarmStatus -ne "active") {
        Write-Step "Initializing Docker Swarm..."
        docker swarm init
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker Swarm initialized successfully"
        } else {
            Write-Error "Failed to initialize Docker Swarm"
            exit 1
        }
    } else {
        Write-Success "Docker Swarm already active"
    }
    
    # Display node info
    Write-Step "Cluster nodes:"
    docker node ls
}

function Build-Images {
    Write-Step "Building Docker images..."
    
    # Build MySQL
    Write-Host "Building MySQL image..."
    docker build -t biedronka-mysql:latest -f docker/mysql/Dockerfile .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build MySQL image"
        exit 1
    }
    
    # Build PrestaShop
    Write-Host "Building PrestaShop image..."
    docker build -t biedronka-prestashop:latest -f docker/prestashop/Dockerfile .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build PrestaShop image"
        exit 1
    }
    
    Write-Success "Images built successfully"
}

function Deploy-Stack {
    Write-Step "Deploying stack '$StackName'..."
    
    docker stack deploy -c $ComposeFile $StackName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Stack deployed successfully"
        
        Write-Step "Waiting for services to start (30 seconds)..."
        Start-Sleep -Seconds 30
        
        Show-Status
    } else {
        Write-Error "Failed to deploy stack"
        exit 1
    }
}

function Update-Stack {
    Write-Step "Updating stack '$StackName'..."
    
    Build-Images
    
    Write-Step "Performing rolling update..."
    docker stack deploy -c $ComposeFile $StackName
    
    Write-Success "Stack updated successfully"
    Show-Status
}

function Scale-Service {
    Write-Step "Scaling PrestaShop to $Replicas replicas..."
    
    docker service scale "${StackName}_prestashop=$Replicas"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Service scaled to $Replicas replicas"
        Show-Status
    } else {
        Write-Error "Failed to scale service"
        exit 1
    }
}

function Stop-Stack {
    Write-Step "Stopping stack '$StackName'..."
    
    docker stack rm $StackName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Stack stopped successfully"
        Write-Host "Note: Volumes are preserved. Use 'cleanup' action to remove them."
    } else {
        Write-Error "Failed to stop stack"
        exit 1
    }
}

function Cleanup-All {
    Write-Step "WARNING: This will remove all data including database!"
    $confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($confirm -ne "yes") {
        Write-Host "Cleanup cancelled"
        return
    }
    
    # Remove stack
    Write-Step "Removing stack..."
    docker stack rm $StackName
    
    # Wait for cleanup
    Write-Step "Waiting for stack removal (30 seconds)..."
    Start-Sleep -Seconds 30
    
    # Remove volumes
    Write-Step "Removing volumes..."
    docker volume rm "${StackName}_mysql_data" -f 2>$null
    
    # Remove images
    Write-Step "Removing images..."
    docker rmi biedronka-mysql:latest biedronka-prestashop:latest -f 2>$null
    
    Write-Success "Cleanup completed"
}

function Show-Status {
    Write-Step "Stack Status:"
    docker stack ls | Select-String -Pattern "NAME|$StackName"
    
    Write-Step "Services:"
    docker stack services $StackName 2>$null
    
    Write-Step "Tasks (Containers):"
    docker stack ps $StackName --no-trunc 2>$null | Select-Object -First 10
    
    Write-Host "`n"
    Write-Host "Access the shop at:" -ForegroundColor Yellow
    Write-Host "  HTTP:  http://localhost:8080" -ForegroundColor Cyan
    Write-Host "  HTTPS: https://localhost" -ForegroundColor Cyan
    Write-Host "  Admin: http://localhost:8080/admin-dev" -ForegroundColor Cyan
    Write-Host "         Email: makajler@szpont.pl" -ForegroundColor Gray
    Write-Host "         Password: password" -ForegroundColor Gray
}

function Test-Deployment {
    Write-Step "Running deployment tests..."
    
    # Test 1: Check if services are running
    Write-Host "Test 1: Checking service status..."
    $services = docker service ls --filter "name=${StackName}" --format "{{.Replicas}}" 2>$null
    if ($services) {
        Write-Success "Services are running"
    } else {
        Write-Error "No services found"
        return
    }
    
    # Test 2: Test database connection
    Write-Host "Test 2: Testing database connection..."
    $containerID = docker ps -q -f "name=${StackName}_prestashop" | Select-Object -First 1
    if ($containerID) {
        $dbTest = docker exec $containerID php -r "try { new PDO('mysql:host=mysql;dbname=prestashop', 'root', 'toor'); echo 'OK'; } catch (Exception `$e) { echo 'FAIL'; }" 2>$null
        if ($dbTest -eq "OK") {
            Write-Success "Database connection successful"
        } else {
            Write-Error "Database connection failed"
        }
    }
    
    # Test 3: Test HTTP endpoint
    Write-Host "Test 3: Testing HTTP endpoint..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 5 2>$null
        if ($response.StatusCode -eq 200) {
            Write-Success "HTTP endpoint responding"
        }
    } catch {
        Write-Error "HTTP endpoint not accessible"
    }
    
    Write-Host "`nDeployment tests completed" -ForegroundColor Green
}

# Main execution
Write-Host "`n╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Biedronka PrestaShop - Swarm Deployer  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan

switch ($Action) {
    'deploy' {
        Initialize-Swarm
        Build-Images
        Deploy-Stack
        Start-Sleep -Seconds 10
        Test-Deployment
    }
    'update' {
        Update-Stack
    }
    'scale' {
        Scale-Service
    }
    'stop' {
        Stop-Stack
    }
    'cleanup' {
        Cleanup-All
    }
    'status' {
        Show-Status
    }
}

Write-Host "`n✨ Done!`n" -ForegroundColor Green
