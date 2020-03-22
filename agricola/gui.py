#coding: utf-8
from future.builtins.misc import input
import re

from agricola.action import (
  DiscreteChoice, CountChoice, ListChoice,
  VariableLengthListChoice, SpaceChoice)
from agricola.ui import UserInterface

from kivy.app import App

class GUI(UserInterface):
  def __init__(self):
    print("init")
    #App().run()
