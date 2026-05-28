import 'package:go_router/go_router.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/auth/phone_otp_screen.dart';
import '../screens/groups/group_list_screen.dart';
import '../screens/groups/group_detail_screen.dart';
import '../screens/auctions/auction_screen.dart';
import '../screens/payments/payment_screen.dart';
import '../screens/reports/reports_screen.dart';
import '../screens/notifications/notifications_screen.dart';
import '../screens/settings_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
    GoRoute(path: '/phone-login', builder: (_, __) => const PhoneOtpScreen()),
    GoRoute(path: '/groups', builder: (_, __) => const GroupListScreen()),
    GoRoute(path: '/groups/:id', builder: (_, state) => GroupDetailScreen(groupId: state.pathParameters['id']!)),
    GoRoute(path: '/auctions/:id', builder: (_, state) => AuctionScreen(auctionId: state.pathParameters['id']!)),
    GoRoute(path: '/payments/:groupId/:month', builder: (_, state) => PaymentScreen(
      groupId: state.pathParameters['groupId']!,
      month: int.parse(state.pathParameters['month']!),
    )),
    GoRoute(path: '/reports/:groupId', builder: (_, state) => ReportsScreen(groupId: state.pathParameters['groupId']!)),
    GoRoute(path: '/notifications', builder: (_, __) => const NotificationsScreen()),
    GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
  ],
);
