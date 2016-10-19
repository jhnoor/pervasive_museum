
def draw_versus_screen(self):
    self.main_layout.add_widget(self.question_grid)
    self.players_grid = PlayersGridLayout(self.game_type)

    for player in persistence.current_players:
        self.player_boxes.append(PlayerLayout(player, self.game_type))

    for player_box in self.player_boxes:
        self.players_grid.add_widget(player_box)

    self.main_layout.add_widget(self.players_grid)
    self.add_widget(self.main_layout)