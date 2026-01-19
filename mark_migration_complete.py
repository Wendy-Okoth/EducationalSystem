# mark_migration_complete.py
from app import create_app, db
from alembic.config import Config
from alembic import command

app = create_app()

def mark_migration_complete():
    with app.app_context():
        print("Marking migration as complete...")
        
        # Create Alembic config
        alembic_cfg = Config("migrations/alembic.ini")
        alembic_cfg.set_main_option("script_location", "migrations")
        
        # Stamp the database with current revision
        command.stamp(alembic_cfg, "head")
        print("✅ Migration marked as complete")
        
        # Verify
        from alembic.migration import MigrationContext
        from alembic.script import ScriptDirectory
        
        context = MigrationContext.configure(db.engine.connect())
        current_rev = context.get_current_revision()
        print(f"Current database revision: {current_rev}")

if __name__ == "__main__":
    mark_migration_complete()