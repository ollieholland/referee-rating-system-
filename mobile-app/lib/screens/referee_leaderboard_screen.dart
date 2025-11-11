import 'package:flutter/material.dart';

class RefereeLeaderboardScreen extends StatelessWidget {
  final List<Map<String, dynamic>> leaderboard = [
    {"referee": "Michael Oliver", "league": "Premier League", "rating": 8.12},
    {"referee": "Daniele Orsato", "league": "Serie A", "rating": 8.02},
    {"referee": "Clément Turpin", "league": "Ligue 1", "rating": 7.88},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Top Referees (Across Leagues)")),
      body: ListView.builder(
        itemCount: leaderboard.length,
        itemBuilder: (context, index) {
          final ref = leaderboard[index];

          return Card(
            elevation: 2,
            margin: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
            child: ListTile(
              title: Text(ref["referee"]),
              subtitle: Text(ref["league"]),
              trailing: Text(ref["rating"].toString()),
            ),
          );
        },
      ),
    );
  }
}
