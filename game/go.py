#!/usr/bin/env python
from copy import deepcopy
from game.util import PointDict
"""
This file is the full backend environment of the game.
"""

BOARD_SIZE = 20  # number of rows/cols = BOARD_SIZE - 1


def opponent_color(color):
    if color == 'WHITE':
        return 'BLACK'
    elif color == 'BLACK':
        return 'WHITE'
    else:
        print('Invalid color: ' + color)
        return KeyError


def neighbors(point):
    """Return a list of neighboring points."""
    neighboring = [(point[0] - 1, point[1]),
                   (point[0] + 1, point[1]),
                   (point[0], point[1] - 1),
                   (point[0], point[1] + 1)]
    return [point for point in neighboring if 0 < point[0] < BOARD_SIZE and 0 < point[1] < BOARD_SIZE]


def cal_liberty(points, board):
    """Find and return the liberties of the point."""
    liberties = [point for point in neighbors(points)
                 if not board.stonedict.get_groups('BLACK', point) and not board.stonedict.get_groups('WHITE', point)]
    return set(liberties)


class Group(object):
    def __init__(self, point, color, liberties):
        """
        Create and initialize a new group.
        :param point: the initial stone in the group
        :param color:
        :param liberties:
        """
        self.color = color
        if isinstance(point, list):
            self.points = point
        else:
            self.points = [point]
        self.liberties = liberties

    @property
    def num_liberty(self):
        return len(self.liberties)

    def add_stones(self, pointlist):
        """Only update stones, not liberties"""
        self.points.extend(pointlist)
    
    def remove_liberty(self, point):
        self.liberties.remove(point)

    def __str__(self):
        """Summarize color, stones, liberties."""
        return '%s - stones: [%s]; liberties: [%s]' % \
               (self.color,
                ', '.join([str(point) for point in self.points]),
                ', '.join([str(point) for point in self.liberties]))
    
    def __repr__(self):
        return str(self)


class Board(object):
    """
    get_legal_actions(), generate_successor_state() are the external game interface.
    put_stone() is the main internal method that contains all logic to update game state.
    create_group(), remove_group(), merge_groups() operations don't check winner or endangered groups.
    Winner or endangered groups are updated in put_stone().
    Winning criteria: remove any opponent's group, or no legal actions for opponent.
    """
    def __init__(self, next_color='BLACK'):
        self.winner = None
        self.next = next_color
        self.legal_actions = []  # Legal actions for current state
        self.end_by_no_legal_actions = False
        self.counter_move = 0

        # Point dict
        self.libertydict = PointDict()  # {color: {point: {groups}}}
        self.stonedict = PointDict()

        # Group list
        self.groups = {'BLACK': [], 'WHITE': []}
        self.endangered_groups = []  # groups with only 1 liberty
        self.removed_groups = []  # This is assigned when game ends
                
    def create_group(self, point, color):
        """Create a new group."""
        # Update group list
        ll = cal_liberty(point, self)
        group = Group(point, color, ll)
        self.groups[color].append(group)
        # Update endangered group
        if len(group.liberties) <= 1:
            self.endangered_groups.append(group)
        # Update stonedict
        self.stonedict.get_groups(color, point).append(group)
        # Update libertydict
        for liberty in group.liberties:
            self.libertydict.get_groups(color, liberty).append(group)
        return group
      
    def remove_group(self, group):
        """
        Remove the group.
        :param group:
        :return:
        """
        color = group.color
        # Update group list
        self.groups[color].remove(group)
        # Update endangered_groups
        if group in self.endangered_groups:
            self.endangered_groups.remove(group)
        # Update stonedict
        for point in group.points:
            self.stonedict.get_groups(color, point).remove(group)
        # Update libertydict
        for liberty in group.liberties:
            self.libertydict.get_groups(color, liberty).remove(group)

    def merge_groups(self, grouplist, point):
        """
        Merge groups (assuming same color).
        all groups already have this liberty removed;
        libertydict already has this point removed.
        :param grouplist:
        :param point:
        """
        color = grouplist[0].color
        newgroup = grouplist[0]
        all_liberties = grouplist[0].liberties

        # Add last move (update newgroup and stonedict)
        newgroup.add_stones([point])
        self.stonedict.get_groups(color, point).append(newgroup)
        all_liberties = all_liberties | cal_liberty(point, self)

        # Merge with other groups (update newgroup and stonedict)
        for group in grouplist[1:]:
            newgroup.add_stones(group.points)
            for p in group.points:
                self.stonedict.get_groups(color, p).append(newgroup)
            all_liberties = all_liberties | group.liberties
            self.remove_group(group)

        # Update newgroup liberties (point is already removed from group liberty)
        newgroup.liberties = all_liberties

        # Update libertydict
        for point in all_liberties:
            belonging_groups = self.libertydict.get_groups(color, point)
            if newgroup not in belonging_groups:
                belonging_groups.append(newgroup)

        return newgroup

    def get_legal_actions(self):
        """External interface to get legal actions"""
        # It is important NOT to calculate actions on the fly to keep the performance.
        return self.legal_actions.copy()

    def _get_legal_actions(self):
        """Internal method to calculate legal actions; shouldn't be called outside"""
        if self.winner:
            return []

        endangered_lbt_self = set()
        endangered_lbt_opponent = set()
        for group in self.endangered_groups:
            if group.color == self.next:
                endangered_lbt_self = endangered_lbt_self | group.liberties
            else:
                endangered_lbt_opponent = endangered_lbt_opponent | group.liberties

        # If there are opponent's endangered points, return these points to win
        if len(endangered_lbt_opponent) > 0:
            return list(endangered_lbt_opponent)

        legal_actions = []
        if len(endangered_lbt_self) > 0:
            # If there are more than one self endangered points, return these points (losing the game)
            if len(endangered_lbt_self) > 1:
                legal_actions = list(endangered_lbt_self)
            # Rescue the sole endangered liberty if existing
            if len(endangered_lbt_self) == 1:
                legal_actions = list(endangered_lbt_self)
        else:
            legal_actions = set()
            for group in self.groups[opponent_color(self.next)]:
                legal_actions = legal_actions | group.liberties
            legal_actions = list(legal_actions)

        # Final check: no suicidal move, either has liberties or any connected self-group has more than this liberty
        legal_actions_filtered = []
        for action in legal_actions:
            if len(cal_liberty(action, self)) > 0:
                legal_actions_filtered.append(action)
            else:
                connected_self_groups = [self.stonedict.get_groups(self.next, p)[0] for p in neighbors(action)
                                         if self.stonedict.get_groups(self.next, p)]
                for self_group in connected_self_groups:
                    if len(self_group.liberties) > 1:
                        legal_actions_filtered.append(action)
                        break

        return legal_actions_filtered

    def _shorten_liberty(self, group, point, color):
        group.remove_liberty(point)
        if group.color != color:  # If opponent's group, check if winning or endangered groups
            if len(group.liberties) == 0:  # The new stone is opponent's, check if winning
                self.removed_groups.append(group)  # Set removed_group
                self.winner = opponent_color(group.color)
            elif len(group.liberties) == 1:
                self.endangered_groups.append(group)

    def shorten_liberty_for_groups(self, point, color):
        """
        Remove the liberty from all belonging groups.
        For opponent's groups, update consequences such as libertydict, winner or endangered group.
        endangered groups for self will be updated in put_stone() after self groups are merged
        :param point:
        :param color:
        :return:
        """
        # Check opponent's groups first
        opponent = opponent_color(color)
        for group in self.libertydict.get_groups(opponent, point):
            self._shorten_liberty(group, point, color)
        self.libertydict.remove_point(opponent, point)  # update libertydict

        # If any opponent's group dies, no need to check self group
        if not self.winner:
            for group in self.libertydict.get_groups(color, point):
                self._shorten_liberty(group, point, color)
        self.libertydict.remove_point(color, point)  # update libertydict
    
    def put_stone(self, point, check_legal=False):
        if check_legal:
            if point not in self.legal_actions:
                print('Error: illegal move, try again.')
                return False
        # If more than 400 moves (which shouldn't happen), print the board for debug
        if self.counter_move > 400:
            print(self)
            raise RuntimeError('More than 400 moves in one game! Board is printed.')

        # Get all self-groups containing this liberty
        self_belonging_groups = self.libertydict.get_groups(self.next, point).copy()

        # Remove the liberty from all belonging groups (with consequences updated such as winner)
        self.shorten_liberty_for_groups(point, self.next)
        self.counter_move += 1
        if self.winner:
            self.next = opponent_color(self.next)
            return True

        # Update groups with the new point
        if len(self_belonging_groups) == 0:  # Create a group for the new stone
            new_group = self.create_group(point, self.next)
        else:  # Merge all self-groups in touch with the new stone
            new_group = self.merge_groups(self_belonging_groups, point)

        # Update whether is endangered group
        # endangered groups for opponent are already updated in shorten_liberty_for_groups
        if new_group in self.endangered_groups and len(new_group.liberties) > 1:
            self.endangered_groups.remove(new_group)
        elif new_group not in self.endangered_groups and len(new_group.liberties) == 1:
            self.endangered_groups.append(new_group)

        self.next = opponent_color(self.next)

        # Update legal_actions; if there are no legal actions for opponent, claim winning
        self.legal_actions = self._get_legal_actions()
        if not self.legal_actions:
            self.winner = opponent_color(self.next)
            self.end_by_no_legal_actions = True

        return True
    
    def generate_successor_state(self, action, check_legal=False):
        board = self.copy()
        board.put_stone(action, check_legal=check_legal)
        return board
        
    def __str__(self):
        str_groups = [str(group) for group in self.groups['BLACK']] + [str(group) for group in self.groups['WHITE']]
        return 'Next: %s\n%s' % (self.next, '\n'.join(str_groups))

    def exist_stone(self, point):
        """To see if a stone has been placed on the board"""
        return len(self.stonedict.get_groups('BLACK', point)) > 0 or len(self.stonedict.get_groups('WHITE', point)) > 0

    def copy(self):
        """Manual copy because of group dependencies across self variables"""
        board = Board(self.next)
        board.winner = self.winner

        group_mapping = {group: deepcopy(group) for group in self.groups['BLACK'] + self.groups['WHITE']}
        board.groups['BLACK'] = [group_mapping[group] for group in self.groups['BLACK']]
        board.groups['WHITE'] = [group_mapping[group] for group in self.groups['WHITE']]

        board.endangered_groups = [group_mapping[group] for group in self.endangered_groups]
        board.removed_groups = [group_mapping[group] for group in self.removed_groups]

        for point, groups in self.libertydict.get_items('BLACK'):
            if groups:
                board.libertydict.set_groups('BLACK', point, [group_mapping[group] for group in groups])
        for point, groups in self.libertydict.get_items('WHITE'):
            if groups:
                board.libertydict.set_groups('WHITE', point, [group_mapping[group] for group in groups])

        for point, groups in self.stonedict.get_items('BLACK'):
            if groups:
                board.stonedict.set_groups('BLACK', point, [group_mapping[group] for group in groups])
        for point, groups in self.stonedict.get_items('WHITE'):
            if groups:
                board.stonedict.set_groups('WHITE', point, [group_mapping[group] for group in groups])

        return board
