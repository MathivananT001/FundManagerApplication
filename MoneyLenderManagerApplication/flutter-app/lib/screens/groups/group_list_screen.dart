import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../providers/group_provider.dart';
import '../../providers/auth_provider.dart';

class GroupListScreen extends StatefulWidget {
  const GroupListScreen({super.key});

  @override
  State<GroupListScreen> createState() => _GroupListScreenState();
}

class _GroupListScreenState extends State<GroupListScreen> {
  @override
  void initState() {
    super.initState();
    context.read<GroupProvider>().loadGroups();
    context.read<AuthProvider>().loadProfile();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Groups'),
        actions: [
          IconButton(icon: const Icon(Icons.notifications), onPressed: () => context.go('/notifications')),
          IconButton(icon: const Icon(Icons.settings), onPressed: () => context.go('/settings')),
        ],
      ),
      body: Consumer<GroupProvider>(
        builder: (context, provider, _) {
          if (provider.groups.isEmpty) {
            return const Center(child: Text('No groups yet. Tap + to create one!'));
          }
          return ListView.builder(
            itemCount: provider.groups.length,
            itemBuilder: (context, index) {
              final group = provider.groups[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                child: ListTile(
                  title: Text(group['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('₹${group['targeting_amount']?.toStringAsFixed(0) ?? '0'} • ${group['member_count']}/${group['member_slots']} members'),
                  trailing: Chip(label: Text(group['status'], style: const TextStyle(fontSize: 12))),
                  onTap: () => context.go('/groups/${group['id']}'),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showCreateGroupDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  void _showCreateGroupDialog(BuildContext context) {
    final nameCtrl = TextEditingController();
    final slotsCtrl = TextEditingController(text: '10');
    final amountCtrl = TextEditingController(text: '5000');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create Group'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'Group Name')),
            const SizedBox(height: 12),
            TextField(controller: slotsCtrl, decoration: const InputDecoration(labelText: 'Members (8-15)'), keyboardType: TextInputType.number),
            const SizedBox(height: 12),
            TextField(controller: amountCtrl, decoration: const InputDecoration(labelText: 'Amount per Person (₹)'), keyboardType: TextInputType.number),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(onPressed: () async {
            await context.read<GroupProvider>().createGroup(
              nameCtrl.text, int.parse(slotsCtrl.text), double.parse(amountCtrl.text), 2.0,
            );
            if (ctx.mounted) Navigator.pop(ctx);
          }, child: const Text('Create')),
        ],
      ),
    );
  }
}
