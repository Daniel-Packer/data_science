import functions as f


pgn = """[Event "Rated Bullet game"]
[Site "https://lichess.org/Wd3L7La9"]
[Date "2020.05.20"]
[Round "-"]
[White "albertosr"]
[Black "bindercommakyle"]
[Result "1-0"]
[UTCDate "2020.05.20"]
[UTCTime "21:21:11"]
[WhiteElo "1474"]
[BlackElo "1467"]
[WhiteRatingDiff "+8"]
[BlackRatingDiff "-7"]
[Variant "Standard"]
[TimeControl "60+0"]
[ECO "C20"]
[Opening "King's Pawn Game: Napoleon Attack"]
[Termination "Time forfeit"]
[Annotator "lichess.org"]

1. e4 e5 2. Qf3  Qf6 3. Bc4 Qxf3 4. Nxf3 Nf6 5. Nxe5 Bc5 6. Bxf7+ Ke7 7. Bc4 Nc6 8. Nf7 Rf8 9. Ng5 h6 10. Nf3 Nxe4 11. O-O d6 12. d3 Nf6 13. Re1+ Kd8 14. Nc3 Nd4 15. Nxd4 Bxd4 16. Nb5 Bb6 17. Nxc7 Kxc7 18. Bf4 Nd7 19. Bxd6+ Kxd6 20. b4 Kc7 21. d4 Nf6 22. d5 Bd4 23. d6+"""


pgn = """[Event "Rated Blitz game"]
[Site "https://lichess.org/oKhL2oJn"]
[Date "2020.05.21"]
[Round "-"]
[White "bindercommakyle"]
[Black "laclau"]
[Result "0-1"]
[UTCDate "2020.05.21"]
[UTCTime "15:22:02"]
[WhiteElo "1580"]
[BlackElo "1631"]
[WhiteRatingDiff "-5"]
[BlackRatingDiff "+14"]
[Variant "Standard"]
[TimeControl "180+2"]
[ECO "A43"]
[Opening "Old Benoni Defense"]
[Termination "Normal"]
[Annotator "lichess.org"]

1. d4 c5  2. c3 d5 3. Nf3 Bf5 4. e3 e6 5. Bb5+ Nd7 6. Ne5 Nf6 7. g4 Bg6 8. g5 a6 9. Nxg6 hxg6 10. gxf6 axb5 11. fxg7 Bxg7 12. Nd2 Qc7 13. Nf3 b4 14. Bd2 bxc3 15. Bxc3 c4 16. Qc2 Nf6 17. a3 Ne4 18. O-O-O O-O-O 19. Ne1 Rxh2 20. Rxh2 Qxh2 21. f3 Qxc2+ 22. Kxc2 Nxc3 23. Kxc3 Kc7 24. Nc2 f5 25. Nb4 Rh8 26. f4 Rh3 27. Kd2 Bh6 28. Nc2 g5 29. fxg5 Bxg5 30. Rg1 Bh6 31. Rg6 Rh2+ 32. Kc3 Kd6 33. a4 Rh3 34. a5 Bxe3 35. Nxe3 Rxe3+ 36. Kd2 Rb3 37. Kc2 b6 38. a6 Rb5 39. a7 Ra5 40. Rg7 Kc6 41. Re7 Kd6 42. Rg7 f4 43. Rf7 b5 44. Rb7 b4 45. Rb6+ Ke7 46. Rb7+ Kf6 47. Rxb4 Rxa7 48. Rb6 Rg7 49. Kd2 Rg2+ 50. Ke1 Rxb2 0-1"""
game = f.get_gameDict(pgn)

exs = f.exchanges_possible(game)

print(exs)
