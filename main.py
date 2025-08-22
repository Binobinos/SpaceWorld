# space_station_cli.py
from typing import Optional, List
from datetime import datetime
import json
import random

from spaceworld import spaceworld


@spaceworld(
    name="spacestation",
    version="1.0.0",
    docs="🚀 Space Station Control CLI - Manage your orbital outpost"
)
def spacestation():
    """Main Space Station control interface"""
    print("🌌 Welcome to Space Station Control System")
    print("Type 'spacestation --help' for available commands")


# Модуль управления системами станции
@spacestation.module(name="systems", docs="Space station systems control")
def systems_module():
    """Monitor and control station systems"""
    print("🛰️  Station systems initialized")


@systems_module.command(name="status", docs="Check station systems status")
def systems_status(detailed: bool = False):
    """Display current station systems status"""
    systems = {
        "life_support": random.choice(["✅ Optimal", "⚠️  Warning", "❌ Critical"]),
        "power": f"🔋 {random.randint(70, 100)}%",
        "oxygen": f"💨 {random.randint(85, 100)}%",
        "temperature": f"🌡️ {random.randint(18, 25)}°C",
        "communication": random.choice(["📡 Connected", "📡 Weak signal", "📡 Offline"])
    }

    print("🛰️  Space Station Systems Status")
    print("=" * 40)

    for system, status in systems.items():
        print(f"{system.replace('_', ' ').title():<15}: {status}")

    if detailed:
        print("\n📊 Detailed Metrics:")
        print(f"Solar panels: {random.randint(80, 95)}% efficiency")
        print(f"Water recycling: {random.randint(75, 90)}%")
        print(f"CO2 scrubbers: {random.randint(85, 98)}% operational")


@systems_module.command(name="power", docs="Manage power systems")
def power_management(
        action: str = "status",
        level: Optional[int] = None,
        system: str = "main"
):
    """Control power distribution"""
    if action == "status":
        print(f"⚡ Power System Status - {system}")
        print(f"Main grid: {random.randint(85, 100)}%")
        print(f"Backup: {random.randint(90, 100)}%")
        print(f"Battery: {random.randint(70, 95)}%")

    elif action == "adjust" and level:
        print(f"🔧 Adjusting {system} power to {level}%")
        print("✅ Power level adjusted successfully")

    elif action == "emergency":
        print("🚨 ACTIVATING EMERGENCY POWER PROTOCOL")
        print("🔋 Backup systems engaged")
        print("✅ Station secure")


# Модуль управления экипажем
@spacestation.module(name="crew", docs="Crew management and monitoring")
def crew_module():
    """Manage space station crew"""
    print("👨‍🚀 Crew management system online")


@crew_module.command(name="list", docs="List all crew members")
def crew_list(status: str = "all"):
    """Display current crew roster"""
    crew = [
        {"name": "Commander Ivanov", "role": "Commander", "status": "🟢 On duty"},
        {"name": "Dr. Chen", "role": "Science Officer", "status": "🔴 Sleeping"},
        {"name": "Engineer Rodriguez", "role": "Systems Engineer", "status": "🟢 On duty"},
        {"name": "Dr. Tanaka", "role": "Medical Officer", "status": "🟡 Exercise"},
        {"name": "Specialist Kim", "role": "Payload Specialist", "status": "🟢 On duty"}
    ]

    print("👨‍🚀 Space Station Crew Roster")
    print("=" * 40)

    for member in crew:
        if status == "all" or member["status"].split()[-1].lower() == status.lower():
            print(f"{member['name']:<20} - {member['role']:<18} {member['status']}")


@crew_module.command(name="schedule", docs="View crew schedule")
def crew_schedule(day: str = "today"):
    """Display crew activity schedule"""
    activities = [
        "08:00 - Morning briefing",
        "09:00 - Scientific experiments",
        "12:00 - Lunch break",
        "13:00 - Maintenance tasks",
        "16:00 - Physical exercise",
        "18:00 - Dinner",
        "20:00 - Personal time",
        "22:00 - Sleep preparation"
    ]

    print(f"📅 Crew Schedule - {day.title()}")
    print("=" * 40)
    for activity in activities:
        print(f"⏰ {activity}")


# Модуль научных экспериментов
@spacestation.module(name="science", docs="Scientific experiments and research")
def science_module():
    """Manage scientific operations"""
    print("🔬 Science module initialized")


@science_module.command(name="experiments", docs="List available experiments")
def list_experiments(category: Optional[str] = None):
    """Display available scientific experiments"""
    experiments = {
        "biology": [
            "Plant growth in microgravity",
            "Protein crystal growth",
            "Microbial adaptation study"
        ],
        "physics": [
            "Fluid dynamics in zero-G",
            "Plasma physics research",
            "Materials science experiments"
        ],
        "astronomy": [
            "Cosmic ray detection",
            "Exoplanet observation",
            "Solar flare monitoring"
        ]
    }

    print("🔬 Available Scientific Experiments")
    print("=" * 50)

    if category and category in experiments:
        print(f"{category.title()} Experiments:")
        for exp in experiments[category]:
            print(f"  • {exp}")
    else:
        for cat, exps in experiments.items():
            print(f"\n{cat.title()}:")
            for exp in exps:
                print(f"  • {exp}")


@science_module.command(name="start", docs="Start a new experiment")
def start_experiment(
        name: str,
        duration: int = 60,
        priority: str = "medium",
        parameters: Optional[str] = None
):
    """Initialize a scientific experiment"""
    print(f"🔬 Starting experiment: {name}")
    print(f"⏱️  Duration: {duration} minutes")
    print(f"🎯 Priority: {priority}")

    if parameters:
        try:
            params = json.loads(parameters)
            print("📋 Custom parameters:")
            for key, value in params.items():
                print(f"  {key}: {value}")
        except:
            print("⚠️  Invalid JSON parameters")

    print("✅ Experiment initiated successfully")
    print(f"📊 Estimated data yield: {random.randint(5, 95)} GB")


# Модуль навигации и ориентации
@spacestation.module(name="navigation", docs="Station navigation and orientation")
def navigation_module():
    """Control station position and orientation"""
    print("🧭 Navigation systems online")


@navigation_module.command(name="position", docs="Get current orbital position")
def get_position(format: str = "simple"):
    """Display current orbital parameters"""
    from math import sin, cos
    import time

    t = time.time()
    altitude = 408 + 10 * sin(t / 1000)  # Колебания орбиты
    latitude = 51.6 * cos(t / 500)
    longitude = 0.0 + t / 100 % 360

    if format == "simple":
        print(f"🛰️  Current Position:")
        print(f"Altitude: {altitude:.1f} km")
        print(f"Latitude: {latitude:.1f}°")
        print(f"Longitude: {longitude:.1f}°")
        print(f"Speed: {7.66:.2f} km/s")

    else:
        print("📡 Detailed Orbital Parameters:")
        print(f"Inclination: 51.6°")
        print(f"Period: 92.68 minutes")
        print(f"Velocity: 7.66 km/s")
        print(f"Orbit: Low Earth Orbit (LEO)")
        print(f"Next ground contact: in {random.randint(15, 45)} minutes")


@navigation_module.command(name="adjust", docs="Adjust station orientation")
def adjust_orientation(
        pitch: float = 0.0,
        yaw: float = 0.0,
        roll: float = 0.0,
        reason: str = "standard"
):
    """Perform orientation maneuver"""
    print(f"🔄 Performing orientation adjustment:")
    print(f"Pitch: {pitch}°")
    print(f"Yaw: {yaw}°")
    print(f"Roll: {roll}°")
    print(f"Reason: {reason}")
    print("✅ Maneuver completed successfully")
    print(f"📊 Fuel consumed: {abs(pitch + yaw + roll) * 0.1:.2f} kg")


# Команды экстренного реагирования
@spacestation.command(name="emergency", docs="Emergency procedures")
def emergency_procedure(
        code: str,
        confirm: bool = False,
        level: str = "1"
):
    """Execute emergency procedures"""
    procedures = {
        "red": "🚨 CRITICAL EMERGENCY - Evacuate to escape pods",
        "yellow": "⚠️  WARNING - Prepare for emergency measures",
        "blue": "🔵 MEDICAL EMERGENCY - Alert medical team",
        "black": "⚫ COMMUNICATIONS FAILURE - Switch to backup",
        "green": "🟢 ALL CLEAR - Resume normal operations"
    }

    if code.lower() in procedures:
        procedure = procedures[code.lower()]
        print(f"EMERGENCY PROTOCOL {code.upper()}")
        print("=" * 50)
        print(procedure)

        if confirm:
            print("\n✅ Protocol confirmed - executing...")
            print("📡 Alerting ground control")
            print("👨‍🚀 Notifying crew")
        else:
            print("\n❌ Confirmation required. Use --confirm")
    else:
        print(f"❌ Unknown emergency code: {code}")
        print("Available codes: red, yellow, blue, black, green")


@spacestation.command(name="log", docs="View station logs")
def view_logs(
        entries: int = 10,
        severity: str = "all",
        system: Optional[str] = None
):
    """Display station operation logs"""
    log_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
    systems = ["life_support", "power", "navigation", "communication", "science"]

    print(f"📋 Last {entries} log entries:")
    print("=" * 60)

    for i in range(entries):
        level = random.choice(log_levels)
        sys = random.choice(systems)
        time = datetime.now().strftime("%H:%M:%S")

        if severity != "all" and level != severity.upper():
            continue

        if system and sys != system:
            continue

        messages = {
            "INFO": ["System nominal", "Routine check completed", "Data recorded"],
            "WARNING": ["Minor fluctuation detected", "Resource levels low", "Anomaly detected"],
            "ERROR": ["System malfunction", "Communication interrupted", "Sensor failure"],
            "CRITICAL": ["CRITICAL FAILURE", "EMERGENCY PROTOCOL INITIATED", "EVACUATE"]
        }

        message = random.choice(messages[level])
        print(f"{time} [{level}] {sys}: {message}")


if __name__ == "__main__":
    spacestation()