# 📌 Application Design Questions

---

## Question 1 of 10  
**Chit Fund Group Lifecycle: Which auction/bidding model should the system enforce?**  
- Sealed-bid auction — members submit bids privately, lowest bid wins each month  
- Open/live auction — members bid in real-time within a time window, lowest bid wins  
- Fixed rotation — no bidding, winner is pre-assigned by rotation order  
- Hybrid — sealed-bid default with option for fund manager to override to fixed rotation  
- Other — please describe  

**Answer:** Open/live auction — real-time bidding, highest bidder wins. If no bids are placed, a random number generator selects the winner from members who have NOT yet received the auction amount in prior months. Every group member pays a monthly contribution = (auction amount won that month) ÷ (total number of members). Bot agent is excluded from all bidding, contribution calculations, and random selection — bot is a management-only participant.  

---

## Question 2 of 10  
**Bot Agent Role: One bot agent is part of each chit fund group. What should the bot agent do?**  
- Auto-bid on behalf of unresponsive members  
- Act as a placeholder slot — takes the last remaining month  
- Send automated reminders and escalations only — no bidding capability  
- Full automation — manage bid strategy, send reminders, and handle payments  
- Other — please describe  

**Answer:** Bot role: Send automated SMS/push reminders to members for auction deadlines and payment due dates. Separately, the system (not the bot) must have a dedicated functionality to randomly select a winner from members who have not yet received the auction amount in previous months — triggered when no bids are placed during an auction.  

---

## Question 3 of 10  
**Auction Timing & Scheduling: How should monthly auctions be triggered and managed?**  
- Fund manager manually opens and closes each auction  
- Automated scheduling — auto-opens on a configured day of month, auto-closes after a set window  
- Hybrid — auto-opens on schedule, but fund manager must manually close/confirm  
- Event-driven — auction opens only when fund manager explicitly triggers it  
- Other — please describe  

**Answer:** Fund manager manually opens and closes each auction per month.  

---

## Question 4 of 10  
**Payment Tracking: How should monthly contribution payments be tracked and verified?**  
- Manual confirmation only — fund manager marks each member's payment as received  
- UPI/bank reference entry — member enters a payment reference ID, fund manager confirms  
- Third-party payment gateway integration (e.g. Razorpay)  
- Hybrid — manual confirmation for now, with payment gateway integration later  
- Other — please describe  

**Answer:** Hybrid — manual confirmation for now, with payment gateway integration as a future phase. Current phase: fund manager manually marks payments as received. Members can attach a description, images/documents (gallery picker), and camera capture as proof of payment. File attachments stored in AWS S3.  

---

## Question 5 of 10  
**Member Defaulter Handling: What happens when a member misses a monthly contribution?**  
- Automated penalty calculation and notification only  
- System locks the defaulting member from bidding in next auction automatically  
- Escalating reminders followed by fund manager alert  
- All of the above combined  
- Other — please describe  

**Answer:** Monthly contribution has a configurable payment deadline (set by fund manager per group/month). If a member misses the deadline: both the fund manager and the defaulting member receive an SMS notification. Fund manager has a dashboard view of all unpaid members and can initiate a direct phone voice call to each defaulting member from within the app (native phone dialer integration). No automatic bid-lock — fund manager handles follow-up manually with the call feature.  

---

## Question 6 of 10  
**API Architecture: Given FastAPI backend + Flutter client, how should the API layer be structured?**  
- Single monolithic FastAPI service  
- Modular monolith — one FastAPI app with separated routers  
- Microservices — separate FastAPI services per domain  
- Serverless-first — Lambda functions per endpoint group  
- Other — please describe  

**Answer:** Microservices — separate FastAPI services per domain (auth-service, group-service, auction-service, payment-service, notification-service), each deployed on ECS Fargate or Lambda. Future migration to Kubernetes is planned — architecture should be container-first to facilitate that transition.  

---

## Question 7 of 10  
**Real-time Features: The app needs auction bidding updates and payment notifications. What real-time mechanism should be used?**  
- Polling — Flutter app polls API  
- WebSockets via API Gateway WebSocket API  
- AWS SNS + FCM push notifications for bid events  
- Hybrid — WebSocket for live, push for background  
- Other — please describe  

**Answer:** WebSockets via AWS API Gateway WebSocket API for real-time bidirectional bid updates during live auctions (auctions typically last 2–3 minutes). Auction flow: (1) Fund manager sets auction time → system sends join invites (push + SMS). (2) Bot tracks attendance — identifies members who have never won before and reports presence/absence. (3) Live auction runs via WebSocket. (4) If no bids, random selection from non-winners who are present (or all non-winners if none present). Background notifications via AWS SNS for members not in the auction screen.  

---

## Question 8 of 10  
**Report Generation: Where should report generation happen?**  
- On-device — Flutter generates reports  
- Server-side — Lambda generates reports, stores in S3  
- Hybrid — summaries in-app, exports via Lambda  
- Third-party reporting service  
- Other — please describe  

**Answer:** Hybrid — simple in-app summaries rendered by Flutter, complex exportable reports (PDF/Excel) generated server-side via dedicated AWS Lambda function + stored in S3, returned to Flutter app as a presigned download URL.  

---

## Question 9 of 10  
**Multi-language Support: Confirmed Tamil + English. How should localization be implemented?**  
- Flutter built-in localization (ARB files)  
- Server-driven localization — strings fetched from backend/S3  
- Hybrid — static UI strings in Flutter, dynamic content localized server-side  
- Third-party localization service  
- Other — please describe  

**Answer:** Server-driven localization — language strings fetched from backend/S3, updatable without an app release. Both Tamil and English UI strings hosted on S3/backend.  

---

## Question 10 of 10  
**Data Archival & Audit: How should completed group data be handled?**  
- Keep all data in RDS indefinitely  
- Archive completed group data to S3, remove from RDS  
- Soft-delete in RDS — mark groups as 'archived'  
- Move to DynamoDB cold storage, retain S3 backup  
- Other — please describe  

**Answer:** Archive completed group data to S3 (as JSON/CSV) after group closes, remove from active RDS MySQL tables. Completed groups accessible via archived data in S3.  
