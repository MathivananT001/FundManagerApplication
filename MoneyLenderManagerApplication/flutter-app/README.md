# MoneyLendingManager — Flutter Mobile App

## Overview
Android-first Flutter application for fund managers and group members to manage chit fund groups, participate in live auctions, track payments, and view reports.

## Setup (First Time)

```bash
cd flutter-app
chmod +x setup.sh
./setup.sh
```

This generates the Android scaffolding via `flutter create` and runs `flutter pub get`.

## Run

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8001 --dart-define=WS_BASE_URL=ws://10.0.2.2:8005
```

(Use `10.0.2.2` for Android emulator to reach host machine)

## Screens

| Screen | Route | Description |
|--------|-------|-------------|
| Login | `/login` | Email/password + Phone OTP + Google |
| Register | `/register` | New user registration |
| Phone OTP | `/phone-login` | Phone number + OTP verification |
| Group List | `/groups` | Fund manager dashboard |
| Group Detail | `/groups/:id` | Members, financials, actions |
| Auction | `/auctions/:id` | Live WebSocket bidding |
| Payments | `/payments/:groupId/:month` | Contribution ledger + confirm |
| Reports | `/reports/:groupId` | PDF/Excel download |
| Notifications | `/notifications` | Notification history |
| Settings | `/settings` | Language toggle (Tamil/English) |

## Architecture
- **State Management**: Provider (ChangeNotifier)
- **Routing**: go_router (declarative)
- **HTTP**: http package + flutter_secure_storage for JWT
- **WebSocket**: web_socket_channel (live auctions)
- **Localization**: Server-driven JSON bundles (Tamil/English)

## Build Release APK
```bash
flutter build apk --release \
  --dart-define=API_BASE_URL=https://YOUR_API_GATEWAY/prod \
  --dart-define=WS_BASE_URL=wss://YOUR_WS_API/prod \
  --dart-define=ENVIRONMENT=prod
```
