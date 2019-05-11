# coding: utf-8
import os, argparse, datetime
from agricola.game import StandardAgricolaGame, TextInterface, play

if __name__ == "__main__":
  now = datetime.datetime.now()

  parser = argparse.ArgumentParser(description='Agricola Simulator')
  parser.add_argument('--agents', nargs=4)
  parser.add_argument('--logdir', default=str(now))
  args = parser.parse_args()

  agent_processes = list(map(lambda p: subprocess.Popen([p], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8'), args.agents))

  os.makedirs(args.logdir, exist_ok=True)

  # game = LessonsAgricolaGame(2)
  # game = SimpleAgricolaGame(2)
  game = StandardAgricolaGame(4, str(uuid.uuid4()))
  ui = TextInterface()
  #ui = GUI()
  play(game, ui, agent_processes, args.logdir)
