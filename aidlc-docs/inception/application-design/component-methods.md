MoneyLendingManager — Component Methods
Method signatures for all major components across backend microservices and the Flutter mobile client.

Auth Service (FastAPI)
# User Registration & Authentication
async def register_user(payload: UserRegistrationRequest) -> UserResponse
async def login_with_email(email: str, password: str) -> TokenResponse
async def login_with_google(google_oauth_token: str) -> TokenResponse
async def login_with_phone_otp(phone_number: str) -> OTPInitiatedResponse
async def verify_phone_otp(phone_number: str, otp_code: str) -> TokenResponse
async def refresh_token(refresh_token: str) -> TokenResponse
async def logout(user_id: str, token: str) -> SuccessResponse

# Profile Management
async def get_user_profile(user_id: str) -> UserProfileResponse
async def update_user_profile(user_id: str, payload: UpdateProfileRequest) -> UserProfileResponse
async def set_language_preference(user_id: str, language: str) -> SuccessResponse  # "en" | "ta"

# Role & Session
async def assign_role(user_id: str, role: UserRole) -> SuccessResponse  # FUND_MANAGER | MEMBER | BOT
async def validate_token(token: str) -> TokenValidationResponse
async def get_session(user_id: str) -> SessionResponse
Group Service (FastAPI)
# Group Lifecycle
async def create_group(payload: CreateGroupRequest, manager_id: str) -> GroupResponse
    # payload: name, member_slots (8-15), contribution_amount_per_person, manager_fee_percent, currency="INR"
async def get_group(group_id: str) -> GroupDetailResponse
async def list_groups_by_manager(manager_id: str) -> List[GroupSummaryResponse]
async def list_groups_by_member(member_id: str) -> List[GroupSummaryResponse]
async def update_group_settings(group_id: str, payload: UpdateGroupRequest) -> GroupResponse
async def activate_group(group_id: str, manager_id: str) -> GroupResponse
async def archive_group(group_id: str, manager_id: str) -> ArchiveGroupResponse
    # Triggers: export to S3 (JSON/CSV) + purge from RDS

# Member Management
async def add_member(group_id: str, member_id: str, manager_id: str) -> GroupMemberResponse
async def remove_member(group_id: str, member_id: str, manager_id: str) -> SuccessResponse
async def get_group_members(group_id: str) -> List[GroupMemberResponse]
async def assign_bot_to_group(group_id: str) -> BotMemberResponse
async def get_non_winners(group_id: str) -> List[GroupMemberResponse]
    # Returns members who have NOT yet received auction amount (excludes bot)
async def mark_member_as_winner(group_id: str, member_id: str, month: int) -> SuccessResponse

# Payment Deadline
async def set_payment_deadline(group_id: str, month: int, deadline_date: date) -> SuccessResponse
async def get_payment_deadline(group_id: str, month: int) -> PaymentDeadlineResponse

# Archival
async def export_group_to_s3(group_id: str) -> S3ArchiveResponse
    # Serializes all group data (members, auctions, payments) to JSON/CSV and uploads to S3
Auction Service (FastAPI + Lambda)
# Auction Lifecycle (REST)
async def schedule_auction(group_id: str, month: int, scheduled_at: datetime, manager_id: str) -> AuctionResponse
    # Stores auction time, triggers join invite dispatch via Notification Service
async def open_auction(auction_id: str, manager_id: str) -> AuctionResponse
    # Sets auction status to OPEN, opens WebSocket room
async def close_auction(auction_id: str, manager_id: str) -> AuctionCloseResponse
    # Declares winner, calculates contributions, notifies Group + Payment services
async def get_auction(auction_id: str) -> AuctionDetailResponse
async def list_auctions_by_group(group_id: str) -> List[AuctionSummaryResponse]
async def get_auction_attendance(auction_id: str) -> AttendanceResponse
    # Returns present/absent breakdown for non-winners

# Bidding
async def place_bid(auction_id: str, member_id: str, bid_amount: float) -> BidResponse
    # Validates: auction is OPEN, member is eligible (not a bot, not already a winner)
    # Broadcasts new highest bid to all WebSocket participants
async def get_current_highest_bid(auction_id: str) -> BidResponse
async def get_bid_history(auction_id: str) -> List[BidResponse]

# Winner Determination
async def determine_winner(auction_id: str) -> WinnerResponse
    # If bids exist: return highest bidder
    # If no bids: random_select_non_winner(group_id, auction_id)
async def random_select_non_winner(group_id: str, auction_id: str) -> WinnerResponse
    # Selects randomly from non-winners present in auction room; if none present, from all non-winners

# Contribution Calculation
async def calculate_monthly_contributions(auction_id: str, winner_id: str) -> List[ContributionRecord]
    # contribution_per_member = auction_amount_received / total_members_excluding_bot

# WebSocket Handlers (API Gateway WebSocket)
async def ws_connect(connection_id: str, auction_id: str, member_id: str) -> None
    # Registers connection in DynamoDB
async def ws_disconnect(connection_id: str) -> None
    # Removes connection from DynamoDB
async def ws_broadcast_bid(auction_id: str, bid: BidResponse) -> None
    # Pushes bid update to all connected participants
async def ws_broadcast_auction_status(auction_id: str, status: AuctionStatus) -> None
    # Broadcasts OPEN / CLOSED / WINNER_DECLARED events
Payment Service (FastAPI)
# Contribution Management
async def get_contribution_ledger(group_id: str, month: int) -> List[ContributionRecord]

async def confirm_payment(payment_id: str, manager_id: str) -> PaymentRecord
    # MANDATORY: Fund manager marks payment as received/confirmed for a member
async def reject_payment(payment_id: str, manager_id: str, reason: str) -> PaymentRecord
    # Fund manager rejects a member's payment claim
async def get_payment_status(group_id: str, member_id: str, month: int) -> PaymentStatusResponse

# Optional Proof Attachments (member-submitted, not mandatory)
async def add_payment_proof(payment_id: str, member_id: str,
                             payload: PaymentProofRequest) -> PaymentProofRecord
    # payload: description (optional text), attachment_urls (optional S3 keys)
    # Proof is additional evidence only; does NOT replace fund manager confirmation
async def generate_upload_presigned_url(group_id: str, member_id: str,
                                         file_name: str, content_type: str) -> PresignedUrlResponse
    # Returns S3 presigned PUT URL for Flutter client to upload optional payment proof directly
async def get_payment_attachments(payment_id: str) -> List[AttachmentResponse]
    # Returns S3 presigned GET URLs for proof images/documents (if any uploaded)

# Defaulter Management
async def get_unpaid_members(group_id: str, month: int) -> List[UnpaidMemberResponse]
    # Returns members whose payment is NOT yet confirmed by fund manager
async def get_member_phone_number(member_id: str) -> PhoneNumberResponse
    # Returns phone number for fund manager to initiate native dialer call
Notification Service (FastAPI + Lambda)
# Dispatch (called by other services)
async def send_sms(phone_number: str, template_key: str, params: dict, language: str) -> NotificationLog
async def send_push_notification(user_id: str, title: str, body: str,
                                  data: dict, language: str) -> NotificationLog
async def send_bulk_sms(phone_numbers: List[str], template_key: str,
                         params: dict, language: str) -> List[NotificationLog]
async def send_bulk_push(user_ids: List[str], title: str, body: str,
                          data: dict, language: str) -> List[NotificationLog]

# Specific Notification Triggers
async def dispatch_auction_invite(auction_id: str, group_id: str) -> None
    # Sends join invite (push + SMS) to all group members when auction is scheduled
async def dispatch_payment_reminder(group_id: str, month: int,
                                     defaulter_user_ids: List[str]) -> None
    # Sends SMS to defaulting member + fund manager (triggered when payment unconfirmed past deadline)
async def dispatch_winner_announcement(auction_id: str, winner_id: str, amount: float) -> None

# Device Token Management
async def register_device_token(user_id: str, fcm_token: str, platform: str) -> SuccessResponse
async def deregister_device_token(user_id: str, fcm_token: str) -> SuccessResponse

# Notification History
async def get_notification_history(user_id: str, limit: int = 50) -> List[NotificationLog]
Report Service (AWS Lambda — Python)
# Report Generation (Lambda handlers)
def generate_group_summary_report(event: ReportRequest) -> ReportResponse
    # Input: group_id, format ("pdf" | "excel")
    # Output: S3 presigned GET URL valid for 15 minutes

def generate_member_history_report(event: ReportRequest) -> ReportResponse
    # Input: group_id, member_id, format ("pdf" | "excel")
    # Output: S3 presigned GET URL

def generate_auction_history_report(event: ReportRequest) -> ReportResponse
    # Input: group_id, format ("pdf" | "excel")
    # Output: S3 presigned GET URL

# Internal helpers
def _build_pdf(data: dict, template: str) -> bytes  # Uses ReportLab
def _build_excel(data: dict) -> bytes               # Uses openpyxl
def _upload_to_s3(content: bytes, key: str, content_type: str) -> str  # Returns S3 key
def _create_presigned_url(s3_key: str, expiry_seconds: int = 900) -> str
Localization Service (S3 + CloudFront)
# Flutter Client Side (Dart)
Future<Map<String, String>> fetchLanguageBundle(String languageCode) async
    # GET {cloudfront_url}/localization/{languageCode}.json
    # Returns key-value map of UI strings

Future<void> setLanguage(String languageCode) async
    # Stores preference in Cognito user profile + local cache

# Server Side (S3 Management — admin CLI/script)
def upload_language_bundle(language_code: str, bundle: dict) -> str
    # Uploads JSON to S3: localization/{language_code}.json
    # Invalidates CloudFront cache for the path
def get_language_bundle(language_code: str) -> dict
    # Reads from S3: localization/{language_code}.json
Bot Agent Component (AWS Lambda — Python)
# Scheduled Triggers (EventBridge)
def run_payment_reminders(event: ScheduledEvent) -> None
    # Queries Payment Service for groups with unconfirmed payments past/near deadline
    # Dispatches SMS/push reminders via Notification Service

def run_auction_reminders(event: ScheduledEvent) -> None
    # Queries Auction Service for upcoming scheduled auctions
    # Dispatches join reminders via Notification Service at T-24h, T-1h

# Event-Driven Triggers (invoked by Auction Service)
def report_pre_auction_attendance(auction_id: str, group_id: str) -> AttendanceSummary
    # Queries DynamoDB WebSocket registry for present members
    # Cross-references with non-winners list from Group Service
    # Returns AttendanceSummary { non_winners_present: [...], non_winners_absent: [...] }
    # Sends summary message to fund manager via Notification Service

# State Tracking
def log_bot_activity(group_id: str, activity_type: str, details: dict) -> None
    # Writes to DynamoDB bot activity log
def get_bot_activity_log(group_id: str, limit: int = 100) -> List[dict]
Flutter Mobile Client — Key Widget/Service Methods (Dart)
// Auth
Future<AuthResult> loginWithGoogle() async
Future<AuthResult> loginWithPhoneOTP(String phoneNumber) async
Future<void> verifyOTP(String phoneNumber, String otp) async
Future<AuthResult> loginWithEmailPassword(String email, String password) async
Future<void> logout() async

// Group
Future<Group> createGroup(CreateGroupParams params) async
Future<List<GroupSummary>> getMyGroups() async
Future<GroupDetail> getGroupDetail(String groupId) async
Future<void> addMember(String groupId, String memberId) async

// Auction
Future<void> joinAuction(String auctionId) async  // Opens WebSocket connection
Future<BidResult> placeBid(String auctionId, double amount) async
Stream<AuctionEvent> auctionEventStream(String auctionId)  // WebSocket stream
Future<void> leaveAuction(String auctionId) async  // Closes WebSocket connection

// Payment
Future<void> confirmPayment(String paymentId) async
    // Fund manager MANDATORY action: marks member payment as received
Future<void> submitOptionalPaymentProof(String paymentId, OptionalProof proof) async
    // Member OPTIONAL action: attach description + images/documents
    // proof: description (optional), attachmentFiles (camera/gallery/docs) — all optional
Future<String> uploadPaymentProof(File file) async
    // Uploads to S3 via presigned URL (only called if member chooses to attach proof)
Future<List<UnpaidMember>> getUnpaidMembers(String groupId, int month) async
void callMember(String phoneNumber)  // Launches native phone dialer (fund manager action)

// Reports
Future<String> downloadReport(String groupId, String type, String format) async
    // Returns presigned S3 URL, triggers in-app browser download

// Notifications
Future<void> registerDeviceToken(String fcmToken) async
Future<List<Notification>> getNotificationHistory() async

// Localization
Future<void> loadLanguageBundle(String languageCode) async
String translate(String key)  // Looks up key in loaded bundle