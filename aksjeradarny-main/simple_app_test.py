#!/usr/bin/env python3
"""
Simple app startup test without model imports
"""

def test_app_creation():
    """Test if we can create the app without errors"""
    print("🧪 TESTING SIMPLE APP CREATION...")
    print("=" * 50)
    
    try:
        # Try to create app without importing models
        from app import create_app
        app = create_app()
        print("✅ App created successfully")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Database URI configured: {'✓' if app.config.get('SQLALCHEMY_DATABASE_URI') else '✗'}")
        
        # Test if we can start the app context
        with app.app_context():
            print("✅ App context works")
            
            # Test basic database connection (without models)
            from app.extensions import db
            print("✅ Database extension initialized")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models_separately():
    """Test model imports separately"""
    print("\n🧪 TESTING MODEL IMPORTS...")
    print("=" * 50)
    
    models = [
        ('User', 'app.models.user'),
        ('Portfolio', 'app.models.portfolio'),
        ('Watchlist', 'app.models.watchlist'),
    ]
    
    for model_name, module_path in models:
        try:
            module = __import__(module_path, fromlist=[model_name])
            model_class = getattr(module, model_name)
            print(f"✅ {model_name}: OK")
        except Exception as e:
            print(f"❌ {model_name}: {e}")

if __name__ == "__main__":
    print("🚀 AKSJERADAR V6 - SIMPLE APP TEST")
    print("=" * 60)
    
    success = test_app_creation()
    test_models_separately()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 BASIC APP CREATION: SUCCESS")
        print("📝 Next step: Try starting the full app with 'python run.py'")
    else:
        print("❌ BASIC APP CREATION: FAILED")
        print("📝 Fix the errors above before proceeding")
    print("=" * 60)
