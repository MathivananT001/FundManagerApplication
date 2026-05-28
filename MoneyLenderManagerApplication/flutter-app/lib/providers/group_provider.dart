import 'package:flutter/material.dart';
import '../services/api_service.dart';

class GroupProvider extends ChangeNotifier {
  List<Map<String, dynamic>> _groups = [];
  Map<String, dynamic>? _currentGroup;

  List<Map<String, dynamic>> get groups => _groups;
  Map<String, dynamic>? get currentGroup => _currentGroup;

  Future<void> loadGroups() async {
    final response = await ApiService.get('/groups');
    _groups = List<Map<String, dynamic>>.from(response);
    notifyListeners();
  }

  Future<void> loadGroupDetail(String groupId) async {
    _currentGroup = await ApiService.get('/groups/$groupId');
    notifyListeners();
  }

  Future<void> createGroup(String name, int memberSlots, double amountPerPerson, double managerFee) async {
    await ApiService.post('/groups', {
      'name': name,
      'member_slots': memberSlots,
      'amount_per_person': amountPerPerson,
      'manager_fee_percent': managerFee,
    });
    await loadGroups();
  }

  Future<void> addMember(String groupId, String userId) async {
    await ApiService.post('/groups/$groupId/members', {'user_id': userId});
    await loadGroupDetail(groupId);
  }
}
