import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../config/app_config.dart';
import '../../services/api_service.dart';

class AuctionScreen extends StatefulWidget {
  final String auctionId;
  const AuctionScreen({super.key, required this.auctionId});

  @override
  State<AuctionScreen> createState() => _AuctionScreenState();
}

class _AuctionScreenState extends State<AuctionScreen> {
  WebSocketChannel? _channel;
  final _bidController = TextEditingController();
  final List<Map<String, dynamic>> _bids = [];
  Map<String, dynamic>? _auction;
  String? _status;

  @override
  void initState() {
    super.initState();
    _loadAuction();
    _connectWebSocket();
  }

  Future<void> _loadAuction() async {
    try {
      final data = await ApiService.get('/auctions/${widget.auctionId}');
      setState(() {
        _auction = data;
        _status = data['status'];
        _bids.addAll(List<Map<String, dynamic>>.from(data['bids'] ?? []));
      });
    } catch (_) {}
  }

  void _connectWebSocket() {
    final uri = Uri.parse('${AppConfig.wsBaseUrl}/auctions/${widget.auctionId}');
    _channel = WebSocketChannel.connect(uri);
    _channel!.stream.listen((message) {
      final event = jsonDecode(message);
      setState(() {
        if (event['event'] == 'NEW_BID') {
          _bids.insert(0, event);
        } else if (event['event'] == 'AUCTION_CLOSED') {
          _status = 'CLOSED';
        }
      });
    });
  }

  Future<void> _placeBid() async {
    final amount = double.tryParse(_bidController.text);
    if (amount == null || amount <= 0) return;
    await ApiService.post('/auctions/${widget.auctionId}/bid', {
      'member_id': 'current-user',
      'bid_amount': amount,
    });
    _bidController.clear();
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Auction #${widget.auctionId.substring(0, 8)}')),
      body: Column(
        children: [
          if (_status != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              color: _status == 'OPEN' ? Colors.green.shade100 : Colors.grey.shade200,
              child: Text('Status: $_status', textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
            ),
          Expanded(
            child: ListView.builder(
              itemCount: _bids.length,
              itemBuilder: (_, i) {
                final bid = _bids[i];
                return ListTile(
                  leading: const Icon(Icons.gavel),
                  title: Text('₹${bid['bid_amount']}'),
                  subtitle: Text(bid['member_id'] ?? ''),
                );
              },
            ),
          ),
          if (_status == 'OPEN')
            Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Expanded(child: TextField(
                    controller: _bidController,
                    decoration: const InputDecoration(labelText: 'Bid Amount (₹)', border: OutlineInputBorder()),
                    keyboardType: TextInputType.number,
                  )),
                  const SizedBox(width: 12),
                  FilledButton(onPressed: _placeBid, child: const Text('Bid')),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
