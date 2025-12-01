#!/bin/bash
# Docker Swarm Deployment Script for Biedronka PrestaShop
# Automates cluster initialization and stack deployment

set -e

STACK_NAME="biedronka"
COMPOSE_FILE="docker/docker-compose.yml"
ACTION="${1:-deploy}"
REPLICAS="${2:-2}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "\n${CYAN}==> $1${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

function initialize_swarm() {
    print_step "Checking Docker Swarm status..."
    
    SWARM_STATUS=$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo "inactive")
    
    if [ "$SWARM_STATUS" != "active" ]; then
        print_step "Initializing Docker Swarm..."
        docker swarm init
        print_success "Docker Swarm initialized successfully"
    else
        print_success "Docker Swarm already active"
    fi
    
    # Display node info
    print_step "Cluster nodes:"
    docker node ls
}

function build_images() {
    print_step "Building Docker images..."
    
    # Build MySQL
    echo "Building MySQL image..."
    docker build -t biedronka-mysql:latest -f docker/mysql/Dockerfile .
    
    # Build PrestaShop
    echo "Building PrestaShop image..."
    docker build -t biedronka-prestashop:latest -f docker/prestashop/Dockerfile .
    
    print_success "Images built successfully"
}

function deploy_stack() {
    print_step "Deploying stack '$STACK_NAME'..."
    
    docker stack deploy -c $COMPOSE_FILE $STACK_NAME
    
    print_success "Stack deployed successfully"
    
    print_step "Waiting for services to start (30 seconds)..."
    sleep 30
    
    show_status
}

function update_stack() {
    print_step "Updating stack '$STACK_NAME'..."
    
    build_images
    
    print_step "Performing rolling update..."
    docker stack deploy -c $COMPOSE_FILE $STACK_NAME
    
    print_success "Stack updated successfully"
    show_status
}

function scale_service() {
    print_step "Scaling PrestaShop to $REPLICAS replicas..."
    
    docker service scale "${STACK_NAME}_prestashop=$REPLICAS"
    
    print_success "Service scaled to $REPLICAS replicas"
    show_status
}

function stop_stack() {
    print_step "Stopping stack '$STACK_NAME'..."
    
    docker stack rm $STACK_NAME
    
    print_success "Stack stopped successfully"
    echo "Note: Volumes are preserved. Use 'cleanup' action to remove them."
}

function cleanup_all() {
    print_step "WARNING: This will remove all data including database!"
    read -p "Are you sure? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "Cleanup cancelled"
        return
    fi
    
    # Remove stack
    print_step "Removing stack..."
    docker stack rm $STACK_NAME || true
    
    # Wait for cleanup
    print_step "Waiting for stack removal (30 seconds)..."
    sleep 30
    
    # Remove volumes
    print_step "Removing volumes..."
    docker volume rm "${STACK_NAME}_mysql_data" -f 2>/dev/null || true
    
    # Remove images
    print_step "Removing images..."
    docker rmi biedronka-mysql:latest biedronka-prestashop:latest -f 2>/dev/null || true
    
    print_success "Cleanup completed"
}

function show_status() {
    print_step "Stack Status:"
    docker stack ls | grep -E "NAME|$STACK_NAME"
    
    print_step "Services:"
    docker stack services $STACK_NAME 2>/dev/null || echo "Stack not deployed"
    
    print_step "Tasks (Containers):"
    docker stack ps $STACK_NAME --no-trunc 2>/dev/null | head -10 || echo "No tasks found"
    
    echo ""
    echo -e "${YELLOW}Access the shop at:${NC}"
    echo -e "${CYAN}  HTTP:  http://localhost:8080${NC}"
    echo -e "${CYAN}  HTTPS: https://localhost${NC}"
    echo -e "${CYAN}  Admin: http://localhost:8080/admin-dev${NC}"
    echo -e "${GRAY}         Email: makajler@szpont.pl${NC}"
    echo -e "${GRAY}         Password: password${NC}"
}

function test_deployment() {
    print_step "Running deployment tests..."
    
    # Test 1: Check if services are running
    echo "Test 1: Checking service status..."
    if docker service ls --filter "name=${STACK_NAME}" --format "{{.Replicas}}" 2>/dev/null | grep -q "."; then
        print_success "Services are running"
    else
        print_error "No services found"
    fi
    
    # Test 2: Test database connection
    echo "Test 2: Testing database connection..."
    CONTAINER_ID=$(docker ps -q -f "name=${STACK_NAME}_prestashop" | head -1)
    if [ -n "$CONTAINER_ID" ]; then
        DB_TEST=$(docker exec $CONTAINER_ID php -r "try { new PDO('mysql:host=mysql;dbname=prestashop', 'root', 'toor'); echo 'OK'; } catch (Exception \$e) { echo 'FAIL'; }" 2>/dev/null || echo "FAIL")
        if [ "$DB_TEST" = "OK" ]; then
            print_success "Database connection successful"
        else
            echo -e "${RED}❌ Database connection failed${NC}"
        fi
    fi
    
    # Test 3: Test HTTP endpoint
    echo "Test 3: Testing HTTP endpoint..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null | grep -q "200"; then
        print_success "HTTP endpoint responding"
    else
        echo -e "${RED}❌ HTTP endpoint not accessible${NC}"
    fi
    
    echo -e "\n${GREEN}Deployment tests completed${NC}"
}

function print_usage() {
    echo "Usage: $0 [ACTION] [REPLICAS]"
    echo ""
    echo "Actions:"
    echo "  deploy   - Initialize Swarm, build images, and deploy stack (default)"
    echo "  update   - Rebuild images and update stack"
    echo "  scale    - Scale PrestaShop service (requires REPLICAS parameter)"
    echo "  stop     - Stop stack (preserves volumes)"
    echo "  cleanup  - Remove everything including volumes"
    echo "  status   - Show current stack status"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 scale 3"
    echo "  $0 status"
    exit 1
}

# Main execution
echo -e "\n${CYAN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Biedronka PrestaShop - Swarm Deployer  ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════╝${NC}"

case "$ACTION" in
    deploy)
        initialize_swarm
        build_images
        deploy_stack
        sleep 10
        test_deployment
        ;;
    update)
        update_stack
        ;;
    scale)
        scale_service
        ;;
    stop)
        stop_stack
        ;;
    cleanup)
        cleanup_all
        ;;
    status)
        show_status
        ;;
    -h|--help|help)
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        print_usage
        ;;
esac

echo -e "\n${GREEN}✨ Done!${NC}\n"
