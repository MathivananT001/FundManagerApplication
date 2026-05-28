import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../providers/group_provider.dart';

class GroupDetailScreen extends StatefulWidget {
  final String groupId;
  const GroupDetailScreen({super.key, required this.groupId});

  @override
  State<GroupDetailScreen> createState() => _GroupDetailScreenState();
}

class _GroupDetailScreenState extends State<GroupDetailScreen> {
  @override
  void initState() {
    super.initState();
    context.read<GroupProvider>().loadGroupDetail(widget.groupId);
  }

  Future<void> _callMember(String phone) async {
    final uri = Uri.parse('tel:$phone');
    if (await canLaunchUrl(uri)) await launchUrl(uri);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Group Details')),
      body: Consumer<GroupProvider>(
        builder: (context, provider, _) {
          final group = provider.currentGroup;
          if (group == null) return const Center(child: CircularProgressIndicator());

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(group['name'], style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _infoRow('Targeting Amount', '₹${group['targeting_amount']?.toStringAsFixed(2)}'),
                        _infoRow('Monthly Auction', '₹${group['monthly_auction_amount']?.toStringAsFixed(2)}'),
                        _infoRow('Members', '${group['member_count']} / ${group['member_slots']}'),
                        _infoRow('Manager Fee', '${group['manager_fee_percent']}%'),
                        _infoRow('Status', group['status']),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text('Members', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                ...(group['members'] as List? ?? []).map((m) => ListTile(
                  leading: Icon(m['role'] == 'MANAGER' ? Icons.star : m['role'] == 'BOT' ? Icons.smart_toy : Icons.person),
                  title: Text(m['user_id']),
                  subtitle: Text(m['role']),
                  trailing: m['has_won'] == true
                      ? Chip(label: Text('Won M${m['won_month']}'))
                      : null,
                )),
                const SizedBox(height: 24),
                // Action buttons
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    FilledButton.icon(
                      onPressed: () => context.go('/auctions/${widget.groupId}'),
                      icon: const Icon(Icons.gavel),
                      label: const Text('Auctions'),
                    ),
                    FilledButton.icon(
                      onPressed: () => context.go('/payments/${widget.groupId}/1'),
                      icon: const Icon(Icons.payment),
                      label: const Text('Payments'),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => context.go('/reports/${widget.groupId}'),
                      icon: const Icon(Icons.assessment),
                      label: const Text('Reports'),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(label, style: TextStyle(color: Colors.grey.shade700)), Text(value, style: const TextStyle(fontWeight: FontWeight.bold))],
      ),
    );
  }
}
