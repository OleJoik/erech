# Erech 🗿

> _“The Dead awaken; for the hour is come for the oathbreakers: at the Stone of Erech they shall stand again and hear there a horn in the hills ringing.”_  
> — *Malbeth the Seer*

**Erech** is a declarative, expressive assertion library for Python, inspired by the style of [Chai.js](https://www.chaijs.com/) and forged in the spirit of Middle-earth.

Named after the **Stone of Erech**, the ancient Númenórean relic upon which oaths were sworn 
and long-awaited reckoning was called, this library is built for readability and expressiveness, 
helping you write tests that read like plain English — with the flowing elegance of Elvish.
No more tests written in plain python, or the cryptic tongue of Mordor (which we will not utter here).
Just as Isildur once bound oathbreakers at the Stone of Erech with a curse that echoed through the ages, 
your tests are bound to declare their intent — and to stand accountable.

## Features

- ✅ Chainable, readable assertions like `should`, `have`, `that`, `match`, and more.
- 🔁 **Multiple assertions** on a single object, in a single `expect().should[...]` expression.
- 🧙 Structured and semantic – makes your tests easier to understand and reason about.
- 📏 Built-in matchers for common types like `uuid`, `email`, etc.

## Example

```python
from erech import expect, have
from uuid import uuid4

expect({
    "gameId": str(uuid4()),
    "userId": str(uuid4()),
    "c": 3
}).should[
    have("gameId").that.matches.uuid,
    have("userId").that.matches.uuid,
]
