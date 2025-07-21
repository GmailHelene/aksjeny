#!/bin/bash
# Set Railway database URL as environment variable

export DATABASE_URL="postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

echo "✅ DATABASE_URL environment variable set"
echo "Now you can run your Python scripts!"

# Run the verification
python3 verify_setup.py
