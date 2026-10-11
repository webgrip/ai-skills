export const CLAIMS = {
  review: {
    status: 'live',
    proof: 'docs/review.md',
    sc: 'steps',
    p: { steps: ['Plan', 'Build', 'Check', 'Explain'] },
    h: { dev: 'Checked *before* you look.', biz: 'Checked, then *signed*.' },
    say: {
      dev: 'A second agent and your own CI check every change before it reaches you.',
      biz: 'Every change is tested and checked, then a named person signs it off.',
    },
  },
  person: {
    status: 'live',
    proof: 'docs/merge.md',
    sc: 'tiles',
    p: { items: [{ t: 'Recorded steps', icon: 'doc' }, { t: 'Your own CI', icon: 'check' }, { t: 'A person merges', icon: 'person' }], cols: 3, hl: [[2]] },
    h: 'A person *decides.*',
    say: { dev: 'Nothing merges until you do.', biz: 'Nothing goes live without a person saying yes.' },
  },
  automerge: {
    status: 'planned',
    proof: 'docs/roadmap.md',
    sc: 'statement',
    p: { items: ['Low-risk changes,', '*merged by rule.*'] },
    say: { dev: 'Next: your own rules let docs-only changes merge by themselves.', biz: 'Next: your own rules let the smallest changes go live by themselves.' },
  },
};

export const HOOKS = {
  'lgtm-speedrun': {
    lines: [
      { vo: 'Four thousand lines. Approved in under a second.', sc: 'slam', p: { words: ['4,000', 'LINES.', 'LGTM.'] } },
    ],
  },
};

export const CLOSES = {
  default: { lines: [{ vo: 'Acme. Agents work. You decide.', sc: 'endcard', p: { a: 'Agents work.', b: 'You decide.' } }] },
};
