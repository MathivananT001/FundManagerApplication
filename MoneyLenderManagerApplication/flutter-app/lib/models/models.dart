class User {
  final String id;
  final String? email;
  final String? phoneNumber;
  final String fullName;
  final String languagePreference;
  final List<String> roles;

  User({required this.id, this.email, this.phoneNumber, required this.fullName,
        required this.languagePreference, required this.roles});

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'], email: json['email'], phoneNumber: json['phone_number'],
    fullName: json['full_name'], languagePreference: json['language_preference'],
    roles: List<String>.from(json['roles'] ?? []),
  );
}

class ChitGroup {
  final String id;
  final String name;
  final String? description;
  final String managerId;
  final int memberSlots;
  final double amountPerPerson;
  final double targetingAmount;
  final double monthlyAuctionAmount;
  final double managerFeePercent;
  final String status;
  final int memberCount;

  ChitGroup({required this.id, required this.name, this.description, required this.managerId,
             required this.memberSlots, required this.amountPerPerson, required this.targetingAmount,
             required this.monthlyAuctionAmount, required this.managerFeePercent,
             required this.status, required this.memberCount});

  factory ChitGroup.fromJson(Map<String, dynamic> json) => ChitGroup(
    id: json['id'], name: json['name'], description: json['description'],
    managerId: json['manager_id'], memberSlots: json['member_slots'],
    amountPerPerson: (json['amount_per_person'] as num).toDouble(),
    targetingAmount: (json['targeting_amount'] as num).toDouble(),
    monthlyAuctionAmount: (json['monthly_auction_amount'] as num).toDouble(),
    managerFeePercent: (json['manager_fee_percent'] as num).toDouble(),
    status: json['status'], memberCount: json['member_count'] ?? 0,
  );
}

class Auction {
  final String id;
  final String groupId;
  final int monthNumber;
  final String status;
  final String? winnerId;
  final double? winningBidAmount;
  final double? disbursementAmount;

  Auction({required this.id, required this.groupId, required this.monthNumber,
           required this.status, this.winnerId, this.winningBidAmount, this.disbursementAmount});

  factory Auction.fromJson(Map<String, dynamic> json) => Auction(
    id: json['id'], groupId: json['group_id'], monthNumber: json['month_number'],
    status: json['status'], winnerId: json['winner_id'],
    winningBidAmount: (json['winning_bid_amount'] as num?)?.toDouble(),
    disbursementAmount: (json['disbursement_amount'] as num?)?.toDouble(),
  );
}

class Contribution {
  final String id;
  final String memberId;
  final int monthNumber;
  final double amountDue;
  final String paymentStatus;

  Contribution({required this.id, required this.memberId, required this.monthNumber,
                required this.amountDue, required this.paymentStatus});

  factory Contribution.fromJson(Map<String, dynamic> json) => Contribution(
    id: json['id'], memberId: json['member_id'], monthNumber: json['month_number'],
    amountDue: (json['amount_due'] as num).toDouble(),
    paymentStatus: json['payment_status'] ?? 'PENDING',
  );
}
