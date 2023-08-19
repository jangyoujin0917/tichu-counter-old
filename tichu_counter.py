import pygame as pg
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt

pg.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
BORDER_COLOR = pg.Color('gray')
FONT = pg.font.Font(None, 32)
isquitted = False


class InputBox:
    # Text Input Box in Pygame
    # https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event, tichu):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    tichu.command(self.text)
                    self.text = ''
                elif event.key == pg.K_DELETE:
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

class Scoreboard:
    def __init__(self, sc_width, sc_height) -> None:
        self.red_score = 0
        self.blue_score = 0
        self.width = sc_width
        self.height = sc_height
        self.red_name = "RED TEAM"
        self.blue_name = "BLUE TEAM"
        self.rect1 = pg.Rect(0, 0, sc_width//2, sc_height*3//10)
        self.rect2 = pg.Rect(sc_width//2, 0, sc_width, sc_height*3//10)

        self.color = pg.Color('black')
        self.score_font = pg.font.Font(None, 70)
        self.red_score_txt = self.score_font.render(str(self.red_score), True, self.color)
        self.blue_score_txt = self.score_font.render(str(self.blue_score), True, self.color)
    
    def add_score(self, red, blue):
        self.red_score += red
        self.blue_score += blue
    
    def rename_red(self, name):
        self.red_name = name
    
    def rename_blue(self, name):
        self.blue_name = name
    
    def draw(self, screen):
        pg.draw.rect(screen, BORDER_COLOR, self.rect1, 1)
        pg.draw.rect(screen, BORDER_COLOR, self.rect2, 1)

        self.red_score_txt = self.score_font.render(str(self.red_score), True, self.color)
        self.blue_score_txt = self.score_font.render(str(self.blue_score), True, self.color)

        text_rect = self.red_score_txt.get_rect(center=(self.width//4, self.height//5))
        screen.blit(self.red_score_txt, text_rect)
        text_rect = self.blue_score_txt.get_rect(center=(self.width*3//4, self.height//5))
        screen.blit(self.blue_score_txt, text_rect)

        team_font = pg.font.Font(None, 50)
        red_team_txt = team_font.render(self.red_name + ' (1, 3)', True, pg.Color('white'), pg.Color('red'))
        blue_team_txt = team_font.render(self.blue_name + ' (2, 4)', True, pg.Color('white'), pg.Color('blue'))
        
        text_rect = red_team_txt.get_rect(center=(self.width//4, self.height//10))
        screen.blit(red_team_txt, text_rect)
        text_rect = blue_team_txt.get_rect(center=(self.width*3//4, self.height//10))
        screen.blit(blue_team_txt, text_rect)

class Roundboard:
    def __init__(self, num) -> None:
        self.num = num
        self.red_score = 0
        self.blue_score = 0
        self.red_tichu = [('',-1),('',-1)] # list of tuples (name, state)
        self.blue_tichu = [('',-1),('',-1)] # 0 - claim, 1 - success, -1 - fail
        self.red_onetwo = False
        self.blue_onetwo = False
    
    def score(self, red_score, blue_score):
        self.red_score += red_score
        self.blue_score += blue_score
        return [self.red_score, self.blue_score]

    def claim(self, type, player):
        if player%2==1:
            self.red_tichu[(player-1)//2] = (type, 0)
        else:
            self.blue_tichu[(player-2)//2] = (type, 0)
    
    def change_state(self, type, player, state):
        if player%2==1 and self.red_tichu[(player-1)//2][0]==type:
            self.red_tichu[(player-1)//2] = (type, state)
            if type=="LT":
                self.red_score += 200*state
            else:
                self.red_score += 100*state
        elif player%2==0 and self.blue_tichu[(player-2)//2][0]==type:
            self.blue_tichu[(player-2)//2] = (type, state)
            if type=="LT":
                self.blue_score += 200*state
            else:
                self.blue_score += 100*state
    
    def onetwo(self, team):
        if team == 1:
            self.red_onetwo = True
            self.red_score += 200
        elif team == 2:
            self.blue_onetwo = True
            self.blue_score += 200
        return [self.red_score, self.blue_score]
    
    def force(self, red_score, blue_score):
        self.red_score = red_score
        self.blue_score = blue_score
        self.red_tichu = [('',-1),('',-1)]
        self.blue_tichu = [('',-1),('',-1)]
    
    def draw(self, screen, y, width, height):
        round_height = height//10

        rect = pg.Rect(0, y, width*4/9, round_height)
        pg.draw.rect(screen, pg.Color('gray'), rect, 1)
        rect = pg.Rect(width*5/9, y, width*4/9, round_height)
        pg.draw.rect(screen, pg.Color('gray'), rect, 1)
        rect = pg.Rect(width*4/9, y, width/9, round_height)
        pg.draw.rect(screen, pg.Color('gray'), rect, 1)

        font = pg.font.Font(None, 50)
        round_num = font.render(str(self.num), True, pg.Color('black'))
        round_num_rect = round_num.get_rect(center=(width/2, y+round_height/2))
        screen.blit(round_num, round_num_rect)

        red_num = font.render(str(self.red_score), True, pg.Color('black'))
        red_num_rect = red_num.get_rect(center=(width/2-width/9, y+round_height/2))
        screen.blit(red_num, red_num_rect)

        blue_num = font.render(str(self.blue_score), True, pg.Color('black'))
        blue_num_rect = blue_num.get_rect(center=(width/2+width/9, y+round_height/2))
        screen.blit(blue_num, blue_num_rect)

        #lt, st expression
        if self.red_tichu[0][0]!='':#player 1 tichu
            color_map = {-1:pg.Color('gray'), 0:pg.Color('black'), 1:pg.Color('red')}
            tichu = font.render(self.red_tichu[0][0]+' 1', True, pg.Color('white'), color_map[self.red_tichu[0][1]])
            tichu_rect = tichu.get_rect(center=(width/9, y+round_height/2))
            screen.blit(tichu, tichu_rect)
        if self.red_tichu[1][0]!='':#player 3 tichu
            color_map = {-1:pg.Color('gray'), 0:pg.Color('black'), 1:pg.Color('red')}
            tichu = font.render(self.red_tichu[1][0]+' 3', True, pg.Color('white'), color_map[self.red_tichu[1][1]])
            tichu_rect = tichu.get_rect(center=(width*2/9, y+round_height/2))
            screen.blit(tichu, tichu_rect)
        if self.blue_tichu[0][0]!='':#player 2 tichu
            color_map = {-1:pg.Color('gray'), 0:pg.Color('black'), 1:pg.Color('blue')}
            tichu = font.render(self.blue_tichu[0][0]+' 2', True, pg.Color('white'), color_map[self.blue_tichu[0][1]])
            tichu_rect = tichu.get_rect(center=(width*7/9, y+round_height/2))
            screen.blit(tichu, tichu_rect)
        if self.blue_tichu[1][0]!='':#player 4 tichu
            color_map = {-1:pg.Color('gray'), 0:pg.Color('black'), 1:pg.Color('blue')}
            tichu = font.render(self.blue_tichu[1][0]+' 4', True, pg.Color('white'), color_map[self.blue_tichu[1][1]])
            tichu_rect = tichu.get_rect(center=(width*8/9, y+round_height/2))
            screen.blit(tichu, tichu_rect)
        
        if self.red_onetwo:
            onetwo = font.render("1/2", True, pg.Color('white'), pg.Color('red'))
            onetwo_rect = onetwo.get_rect(center=(width*3/9, y+round_height/2))
            screen.blit(onetwo, onetwo_rect)
        if self.blue_onetwo:
            onetwo = font.render("1/2", True, pg.Color('white'), pg.Color('blue'))
            onetwo_rect = onetwo.get_rect(center=(width*6/9, y+round_height/2))
            screen.blit(onetwo, onetwo_rect)
    
    def to_dict(self): # for stats
        tmp = {}
        tmp["red_score"] = self.red_score
        tmp["blue_score"] = self.blue_score

        rt = []
        if self.red_tichu[0][0]!='':
            rt.append(self.red_tichu[0][0]+" "+("success" if self.red_tichu[0][1]==1 else "fail"))
        if self.red_tichu[1][0]!='':
            rt.append(self.red_tichu[1][0]+" "+("success" if self.red_tichu[1][1]==1 else "fail"))
        tmp["red_tichu"] = " / ".join(rt)
        bt = []
        if self.blue_tichu[0][0]!='':
            bt.append(self.blue_tichu[0][0]+" "+("success" if self.blue_tichu[0][1]==1 else "fail"))
        if self.blue_tichu[1][0]!='':
            bt.append(self.blue_tichu[1][0]+" "+("success" if self.blue_tichu[1][1]==1 else "fail"))
        tmp["blue_tichu"] = " / ".join(bt)

        tmp["red_onetwo"] = '1/2' if self.red_onetwo else ''
        tmp["blue_onetwo"] = '1/2' if self.blue_onetwo else ''
        return tmp
        
class Historyboard:
    def __init__(self, sc_width, sc_height) -> None:
        self.width = sc_width
        self.height = sc_height
        self.round_height = sc_height//10
        self.round_arr = []
        self.new_blank_round()

    def new_blank_round(self):
        self.round_arr.append(Roundboard(len(self.round_arr)+1))

    def force(self, red_score, blue_score):
        self.round_arr[-1].force(red_score, blue_score)
        self.new_blank_round()
    
    def claim(self, type, player):
        self.round_arr[-1].claim(type, player)
    
    def change_state(self, type, player, state):
        self.round_arr[-1].change_state(type, player, state)

    def score(self, red_score, blue_score):
        total_rs, total_bs = self.round_arr[-1].score(red_score, blue_score)
        self.new_blank_round()
        return [total_rs, total_bs]
    
    def onetwo(self, team):
        red_score, blue_score = self.round_arr[-1].onetwo(team)
        self.new_blank_round()
        return [red_score, blue_score]
    
    def draw(self, screen):
        start_height = self.height*3//10
        for i in range(5):
            if len(self.round_arr)-i > 0:
                self.round_arr[-i-1].draw(screen, start_height, self.width, self.height)
            start_height += self.round_height
    
    def history(self):
        stats_arr = []
        rs = 0
        bs = 0
        for round in self.round_arr[:-1]:
            d = round.to_dict()
            rs += d["red_score"]
            bs += d["blue_score"]
            tmp_arr = [d["red_onetwo"], d["red_tichu"], d["red_score"], rs, '', bs, d["blue_score"], d["blue_tichu"], d["blue_onetwo"]]
            stats_arr.append(tmp_arr)
        return stats_arr
    
    def stats(self):
        stats_arr = [] # score, lt rate, st rate, onetwo count, max_score
        red_score = sum([i.red_score for i in self.round_arr])
        blue_score = sum([i.blue_score for i in self.round_arr])
        stats_arr.append([red_score, blue_score])

        red_tichu = []
        blue_tichu = []
        for i in self.round_arr:
            red_tichu.extend(i.red_tichu)
            blue_tichu.extend(i.blue_tichu)
        red_lt = [len([x for x in red_tichu if x==("LT", 1)]), len([x for x in red_tichu if x[0]=="LT"])]
        blue_lt = [len([x for x in blue_tichu if x==("LT", 1)]), len([x for x in blue_tichu if x[0]=="LT"])]
        red_st = [len([x for x in red_tichu if x==("ST", 1)]), len([x for x in red_tichu if x[0]=="ST"])]
        blue_st = [len([x for x in blue_tichu if x==("ST", 1)]), len([x for x in blue_tichu if x[0]=="ST"])]
        def transform(x):
            if x[1]==0:
                return "-"
            return f"{(x[0]/x[1]*100):0.1f}% ({x[0]} / {x[1]})"
        stats_arr.append([transform(red_lt), transform(blue_lt)])
        stats_arr.append([transform(red_st), transform(blue_st)])

        stats_arr.append([sum(x.red_onetwo for x in self.round_arr), sum(x.blue_onetwo for x in self.round_arr)])

        red_score = max([i.red_score for i in self.round_arr])
        blue_score = max([i.blue_score for i in self.round_arr])
        stats_arr.append([red_score, blue_score])

        return stats_arr


class Tichu:
    def __init__(self, sc_width, sc_height) -> None:
        self.width = sc_width
        self.height = sc_height
        self.scoreboard = Scoreboard(sc_width, sc_height)
        self.historyboard = Historyboard(sc_width, sc_height)
        self.cmd_history = []

    def command(self, cmd):
        contents = cmd.split(" ")
        if(cmd == "undo" and len(self.cmd_history)>0):
            self.cmd_history.pop()
            self.scoreboard = Scoreboard(self.width, self.height)
            self.historyboard = Historyboard(self.width, self.height)
            cmd_history = self.cmd_history
            self.cmd_history = []
            for c in cmd_history:
                self.command(c)
        elif(contents[0] == "rename" and (contents[1] in ["red", "blue"]) and len(contents)>=3):
            name = ' '.join(contents[2:])
            if(contents[1] == "red"):
                self.scoreboard.rename_red(name)
            else:
                self.scoreboard.rename_blue(name)
        elif(contents[0] == "force" and len(contents)==3 and contents[1].lstrip("-").isdecimal() and contents[2].lstrip("-").isdecimal()):
            self.scoreboard.add_score(int(contents[1]), int(contents[2]))
            self.historyboard.force(int(contents[1]), int(contents[2]))
            self.cmd_history.append(cmd)
        elif(contents[0] == "lt" and len(contents)==3 and (contents[1] in ["claim", "success", "fail"]) and (contents[2] in ['1','2','3','4'])): # lt [claim, success, fail] 1
            self.cmd_history.append(cmd)
            if(contents[1] == "claim"):
                self.historyboard.claim("LT", int(contents[2]))
            elif(contents[1] == "success"):
                self.historyboard.change_state("LT", int(contents[2]), 1)
            elif(contents[1] == "fail"):
                self.historyboard.change_state("LT", int(contents[2]), -1)
            else:
                self.cmd_history.pop()
        elif(contents[0] == "st" and len(contents)==3 and (contents[1] in ["claim", "success", "fail"]) and (contents[2] in ['1','2','3','4'])):
            self.cmd_history.append(cmd)
            if(contents[1] == "claim"):
                self.historyboard.claim("ST", int(contents[2]))
            elif(contents[1] == "success"):
                self.historyboard.change_state("ST", int(contents[2]), 1)
            elif(contents[1] == "fail"):
                self.historyboard.change_state("ST", int(contents[2]), -1)
            else:
                self.cmd_history.pop()
        elif(len(contents)==2 and contents[0] in ["stc", "sts", "stf", "ltc", "lts", "ltf"]):
            conversion = {"stc":"st claim", "sts":"st success", "stf":"st fail", "ltc":"lt claim", "lts":"lt success", "ltf":"lt fail"}
            self.command(conversion[contents[0]]+" "+contents[1])
        elif(contents[0] == "score" and len(contents)==3 and contents[1].lstrip("-").isdecimal() and contents[2].lstrip("-").isdecimal()): # total score to scoreboard
            red_score, blue_score = self.historyboard.score(int(contents[1]), int(contents[2]))
            self.scoreboard.add_score(red_score, blue_score)
            self.cmd_history.append(cmd)
        elif(contents[0] == "score" and len(contents)==3 and (contents[1] in ["red", "blue"]) and contents[2].lstrip("-").isdecimal()): # total score to scoreboard - alias
            score = int(contents[2])
            red_score = score if contents[1]=="red" else 100-score
            blue_score = score if contents[1]=="blue" else 100-score
            self.command("score "+str(red_score)+" "+str(blue_score))
        elif(cmd == "onetwo red"):
            red_score, blue_score = self.historyboard.onetwo(1)
            self.scoreboard.add_score(red_score, blue_score)
            self.cmd_history.append(cmd)
        elif(cmd == "onetwo blue"):
            red_score, blue_score = self.historyboard.onetwo(2)
            self.scoreboard.add_score(red_score, blue_score)
            self.cmd_history.append(cmd)
        elif(cmd == "end"): # if end, save history
            now = datetime.datetime.now()
            filename = now.strftime('%Y%m%d-%H%M%S-tichu-history')
            self.command("end "+filename)
        elif(len(contents)==2 and contents[0] == "end"):
            filename = contents[1]
            os.makedirs("history/"+filename)
            with open("history/"+filename+"/cmd_history.txt", 'w+') as f:
                f.write('\n'.join(self.cmd_history))
            
            history = self.historyboard.history()
            stats = self.historyboard.stats()
            with pd.ExcelWriter("history/"+filename+"/statistics.xlsx", engine='xlsxwriter') as writer:
                df = pd.DataFrame(history)
                df.index = [i+1 for i in range(len(df.index))]
                df.columns = ["RED_ONETWO", "RED_TICHU", "RED_ROUND", self.scoreboard.red_name, "VS", self.scoreboard.blue_name, "BLUE_ROUND", "BLUE_TICHU", "BLUE_ONETWO"]
                df.to_excel(writer, "History")

                history_sheet = writer.sheets["History"]
                history_sheet.set_column(0, 9, 15)
                history_sheet.set_column(2, 2, 22)
                history_sheet.set_column(8, 8, 22)
                history_sheet.set_column(5, 5, 6)

                df2 = pd.DataFrame(stats)
                df2.index = ["SCORE", "LT RATE", "ST RATE", "ONETWO", "MAX"]
                df2.columns = [self.scoreboard.red_name, self.scoreboard.blue_name]
                df2.to_excel(writer, "Stats")
                stats_sheet = writer.sheets["Stats"]
                stats_sheet.set_column(0, 2, 10)

                red_score = [0]+df[self.scoreboard.red_name].tolist()
                blue_score = [0]+df[self.scoreboard.blue_name].tolist()
                rounds = list(range(len(red_score)))
                plt.plot(rounds, red_score, 'r', label=self.scoreboard.red_name)
                plt.plot(rounds, blue_score, 'b', label=self.scoreboard.blue_name)
                plt.xlabel('ROUND')
                plt.ylabel('SCORE')
                plt.title(filename)
                plt.legend([self.scoreboard.red_name, self.scoreboard.blue_name])
                plt.xticks(rounds)
                plt.savefig("history/"+filename+"/graph.png")

        elif(cmd == "quit"):
            self.command("end")
            global isquitted
            isquitted = True
        print(cmd)

    def draw(self, screen):
        self.scoreboard.draw(screen)
        self.historyboard.draw(screen)

def main():
    clock = pg.time.Clock()
    cmd_line_txt = FONT.render("Cmd line : ", True, pg.Color('black'))
    author_txt = FONT.render("Made by @jangyoujin0917", True, pg.Color('black'))
    input_box1 = InputBox(220, 670, 500, 32)
    input_boxes = [input_box1]
    tichu = Tichu(SCREEN_WIDTH, SCREEN_HEIGHT)
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for box in input_boxes:
                box.handle_event(event, tichu)
        
        if isquitted:
            break

        for box in input_boxes:
            box.update()

        screen.fill("white")
        for box in input_boxes:
            box.draw(screen)
        tichu.draw(screen)
        screen.blit(cmd_line_txt, (100, 670+5))
        screen.blit(author_txt, (800, 670+5))

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
    pg.quit()