import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../services/api_service.dart';

class PaymentScreen extends StatefulWidget {
  final String groupId;
  final int month;
  const PaymentScreen({super.key, required this.groupId, required this.month});

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  List<Map<String, dynamic>> _ledger = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadLedger();
  }

  Future<void> _loadLedger() async {
    try {
      final data = await ApiService.get('/payments/${widget.groupId}/${widget.month}');
      setState(() { _ledger = List<Map<String, dynamic>>.from(data); _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _confirmPayment(String paymentId) async {
    await ApiService.post('/payments/$paymentId/confirm', {'manager_id': 'current-user'});
    _loadLedger();
  }

  Future<void> _callMember(String phone) async {
    final uri = Uri.parse('tel:$phone');
    if (await canLaunchUrl(uri)) await launchUrl(uri);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Payments — Month ${widget.month}')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _ledger.length,
              itemBuilder: (_, i) {
                final item = _ledger[i];
                final status = item['payment_status'] ?? 'PENDING';
                return ListTile(
                  title: Text('Member: ${item['member_id']}'),
                  subtitle: Text('₹${item['amount_due']} • $status'),
                  trailing: status == 'PENDING'
                      ? IconButton(icon: const Icon(Icons.check_circle, color: Colors.green), onPressed: () => _confirmPayment(item['id']))
                      : const Icon(Icons.done_all, color: Colors.grey),
                );
              },
            ),
    );
  }
}
