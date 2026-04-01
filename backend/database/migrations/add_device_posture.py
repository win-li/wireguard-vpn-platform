"""
Database migration: Add device_posture and device_alerts tables
Run with: python -m database.migrations.add_device_posture
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import engine, Base
from models.device_posture import DevicePosture, DeviceAlert

def upgrade():
    """Create device posture tables"""
    print("Creating device_postures table...")
    Base.metadata.create_all(bind=engine, tables=[DevicePosture.__table__])
    print("Created device_postures table")
    
    print("Creating device_alerts table...")
    Base.metadata.create_all(bind=engine, tables=[DeviceAlert.__table__])
    print("Created device_alerts table")
    
    print("Migration complete!")

def downgrade():
    """Drop device posture tables"""
    print("Dropping device_alerts table...")
    DeviceAlert.__table__.drop(engine, checkfirst=True)
    
    print("Dropping device_postures table...")
    DevicePosture.__table__.drop(engine, checkfirst=True)
    
    print("Rollback complete!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--downgrade", action="store_true", help="Rollback migration")
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()
