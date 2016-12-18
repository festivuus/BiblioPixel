from . base import BaseAnimation


class AnimationQueue(BaseAnimation):

    def __init__(self, led, anims=None):
        super().__init__(led)
        self.anims = anims or []
        self.curAnim = None
        self.animIndex = 0
        self._internalDelay = 0  # never wait
        self.fps = None
        self.untilComplete = False

    # overriding to handle all the animations
    def stopThread(self, wait=False):
        for a, r in self.anims:
            # a bit of a hack. they aren't threaded, but stops them anyway
            a._stopEvent.set()
        super().stopThread(wait)

    def addAnim(self, anim, amt=1, fps=None, max_steps=0, untilComplete=False,
                max_cycles=0, seconds=None):
        a = (
            anim,
            {
                "amt": amt,
                "fps": fps,
                "max_steps": max_steps,
                "untilComplete": untilComplete,
                "max_cycles": max_cycles,
                "seconds": seconds
            }
        )
        self.anims.append(a)

    def preRun(self, amt=1):
        if len(self.anims) == 0:
            raise Exception("Must provide at least one animation.")
        self.animIndex = -1

    def run(self, amt=1, fps=None, sleep=None, max_steps=0, untilComplete=False,
            max_cycles=0, threaded=False, joinThread=False, callback=None,
            seconds=None):
        self.fps = fps
        self.untilComplete = untilComplete
        super().run(amt=1, fps=None, sleep=None, max_steps=0,
                    untilComplete=untilComplete,
                    max_cycles=0, threaded=threaded, joinThread=joinThread,
                    callback=callback, seconds=seconds)

    def step(self, amt=1):
        self.animIndex += 1
        if self.animIndex >= len(self.anims):
            if self.untilComplete:
                self.animComplete = True
            else:
                self.animIndex = 0

        if not self.animComplete:
            self.curAnim = self.anims[self.animIndex]

            anim, run = self.curAnim
            run.update(threaded=False, joinThread=False, callback=None)

            run['fps'] = run.get('fps') or self.fps
            anim.run(**(run))

    RUN_PARAMS = [{
        'id': 'fps',
        'label': 'Default Framerate',
        'type': 'int',
        'default': None,
        'min': 1,
        'help': 'Default framerate to run all animations in queue.'
    }, {
        'id': 'untilComplete',
        'label': 'Until Complete',
        'type': 'bool',
        'default': False,
        'help': 'Run until animation marks itself as complete. If supported.'
    }]
