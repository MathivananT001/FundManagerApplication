#!/bin/bash
# Flutter App Setup Script
# Generates Flutter project scaffolding and copies application code into it.
#
# Usage: ./setup.sh
# Prerequisites: Flutter SDK >= 3.3.0 installed

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMP_DIR=$(mktemp -d)
APP_NAME="money_lending_manager"

echo "=== Creating Flutter project scaffolding ==="
flutter create --org com.moneylender --project-name $APP_NAME "$TEMP_DIR/$APP_NAME"

echo "=== Copying scaffolding into project ==="
# Copy android/, ios/, web/, test/, analysis_options.yaml
cp -r "$TEMP_DIR/$APP_NAME/android" "$SCRIPT_DIR/"
cp -r "$TEMP_DIR/$APP_NAME/test" "$SCRIPT_DIR/"
cp "$TEMP_DIR/$APP_NAME/analysis_options.yaml" "$SCRIPT_DIR/"
cp "$TEMP_DIR/$APP_NAME/.gitignore" "$SCRIPT_DIR/"
cp "$TEMP_DIR/$APP_NAME/.metadata" "$SCRIPT_DIR/"

echo "=== Applying pubspec.yaml ==="
# Our pubspec.yaml is already in place — just run pub get
cd "$SCRIPT_DIR"
flutter pub get

echo "=== Cleanup ==="
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Flutter app ready!"
echo "   Run: cd $(basename $SCRIPT_DIR) && flutter run"
