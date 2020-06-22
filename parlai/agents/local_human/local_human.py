#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Agent does gets the local keyboard input in the act() function.

Example: python examples/eval_model.py -m local_human -t babi:Task1k:1 -dt valid
"""

from parlai.core.agents import Agent
from parlai.core.message import Message
from parlai.utils.misc import display_messages, load_cands
from parlai.utils.strings import colorize


class LocalHumanAgent(Agent):
    def add_cmdline_args(argparser):
        """
        Add command-line arguments specifically for this agent.
        """
        agent = argparser.add_argument_group('Local Human Arguments')
        agent.add_argument(
            '-fixedCands',
            '--local-human-candidates-file',
            default=None,
            type=str,
            help='File of label_candidates to send to other agent',
        )
        agent.add_argument(
            '--single_turn',
            type='bool',
            default=False,
            help='If on, assumes single turn episodes.',
        )

    def __init__(self, opt, shared=None):
        super().__init__(opt)
        self.id = 'localHuman'
        self.episodeDone = False
        self.finished = False
        self.fixedCands_txt = load_cands(self.opt.get('local_human_candidates_file'))
        print(
            colorize(
                "Enter [DONE] if you want to end the episode, [EXIT] to quit.",
                'highlight',
            )
        )

    def epoch_done(self):
        return self.finished

    def observe(self, msg):
        print(
            display_messages(
                [msg],
                ignore_fields=self.opt.get('display_ignore_fields', ''),
                prettify=self.opt.get('display_prettify', False),
            )
        )

    def act(self):
        reply = Message()
        reply['id'] = self.getID()
        try:
            reply_text = input(colorize("Enter Your Message:", 'text') + ' ')
        except EOFError:
            self.finished = True
            return {'episode_done': True}

        reply_text = reply_text.replace('\\n', '\n')
        reply['episode_done'] = False
        if self.opt.get('single_turn', False):
            reply.force_set('episode_done', True)
        reply['label_candidates'] = self.fixedCands_txt
        if '[DONE]' in reply_text:
            # let interactive know we're resetting
            raise StopIteration
        reply['text'] = reply_text
        if '[EXIT]' in reply_text:
            self.finished = True
            raise StopIteration
        return reply

    def episode_done(self):
        return self.episodeDone


class AutoQueryAgent(Agent):
    def add_cmdline_args(argparser):
        """
        Add command-line arguments specifically for this agent.
        """
        agent = argparser.add_argument_group('Local Human Arguments')
        agent.add_argument(
            '-fixedCands',
            '--local-human-candidates-file',
            default=None,
            type=str,
            help='File of label_candidates to send to other agent',
        )
        agent.add_argument(
            '--single_turn',
            type='bool',
            default=False,
            help='If on, assumes single turn episodes.',
        )

    def __init__(self, opt, shared=None, query_txt=None):
        super().__init__(opt)
        self.id = 'localHuman'
        self.episodeDone = False
        self.finished = False
        self.fixedCands_txt = load_cands(self.opt.get('local_human_candidates_file'))
        # utilizing given query text
        self.query_txt = self.make_txt_readable(query_txt)
        self.line_no = 0
        print(
            colorize(
                "Enter [DONE] if you want to end the episode, [EXIT] to quit.",
                'highlight',
            )
        )

    def epoch_done(self):
        return self.finished

    def observe(self, msg):
        print(
            display_messages(
                [msg],
                ignore_fields=self.opt.get('display_ignore_fields', ''),
                prettify=self.opt.get('display_prettify', False),
            )
        )

    def make_txt_readable(self, query_txt) :
        with open(query_txt, "r") as f :
            parsed_txt = f.read().split("\n")[:-1]
        print(parsed_txt)
        return parsed_txt

    def act(self):
        reply = Message()
        reply['id'] = self.getID()
        try:
#            reply_text = input(colorize("Enter Your Message:", 'text') + ' ')
            reply_text = self.query_txt[self.line_no]
            self.line_no += 1
#            if reply_text == '[EXIT]' :
#                self.finished = True
#                raise StopIteration
        except EOFError:
            self.finished = True
            return {'episode_done': True}

        reply_text = reply_text.replace('\\n', '\n')
        reply['episode_done'] = False
        if self.opt.get('single_turn', False):
            reply.force_set('episode_done', True)
        reply['label_candidates'] = self.fixedCands_txt
        if '[DONE]' in reply_text:
            # let interactive know we're resetting
            self.line_no = 0
            raise StopIteration
        reply['text'] = reply_text
        if '[EXIT]' in reply_text:
            self.line_no = 0
            self.finished = True
            raise StopIteration
        if self.line_no >= len(self.query_txt) :
            self.line_no = 0
            self.finished = True
            raise StopIteration

        return reply

    def episode_done(self):
        return self.episodeDone
