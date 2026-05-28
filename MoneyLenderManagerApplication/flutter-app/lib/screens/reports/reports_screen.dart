import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../services/api_service.dart';

class ReportsScreen extends StatelessWidget {
  final String groupId;
  const ReportsScreen({super.key, required this.groupId});

  Future<void> _generateReport(BuildContext context, String type, String format) async {
    try {
      final response = await ApiService.post('/reports/$type', {
        'group_id': groupId,
        'format': format,
      });
      final url = response['download_url'];
      if (url != null) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Reports')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _ReportTile(
            title: 'Group Summary',
            subtitle: 'Overview of group financials and members',
            onPdf: () => _generateReport(context, 'group-summary', 'pdf'),
            onExcel: () => _generateReport(context, 'group-summary', 'excel'),
          ),
          _ReportTile(
            title: 'Auction History',
            subtitle: 'All auctions with winners and amounts',
            onPdf: () => _generateReport(context, 'auction-history', 'pdf'),
            onExcel: () => _generateReport(context, 'auction-history', 'excel'),
          ),
        ],
      ),
    );
  }
}

class _ReportTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onPdf;
  final VoidCallback onExcel;

  const _ReportTile({required this.title, required this.subtitle, required this.onPdf, required this.onExcel});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(icon: const Icon(Icons.picture_as_pdf, color: Colors.red), onPressed: onPdf, tooltip: 'PDF'),
            IconButton(icon: const Icon(Icons.table_chart, color: Colors.green), onPressed: onExcel, tooltip: 'Excel'),
          ],
        ),
      ),
    );
  }
}
