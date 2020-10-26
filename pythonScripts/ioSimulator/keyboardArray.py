from pynput.keyboard import Listener, Key, KeyCode

keyArray = [
#lower case letters
	KeyCode.from_char("a"),
	KeyCode.from_char("b"),
	KeyCode.from_char("c"),
	KeyCode.from_char("d"),
	KeyCode.from_char("e"),
	KeyCode.from_char("f"),
	KeyCode.from_char("g"),
	KeyCode.from_char("h"),
	KeyCode.from_char("i"),
	KeyCode.from_char("j"),
	KeyCode.from_char("k"),
	KeyCode.from_char("l"),
	KeyCode.from_char("m"),
	KeyCode.from_char("n"),
	KeyCode.from_char("o"),
	KeyCode.from_char("p"),
	KeyCode.from_char("q"),
	KeyCode.from_char("r"),
	KeyCode.from_char("s"),
	KeyCode.from_char("t"),
	KeyCode.from_char("u"),
	KeyCode.from_char("v"),
	KeyCode.from_char("w"),
	KeyCode.from_char("x"),
	KeyCode.from_char("y"),
	KeyCode.from_char("z"),
#uppder case letters
	KeyCode.from_char("A"),
	KeyCode.from_char("B"),
	KeyCode.from_char("C"),
	KeyCode.from_char("D"),
	KeyCode.from_char("E"),
	KeyCode.from_char("F"),
	KeyCode.from_char("G"),
	KeyCode.from_char("H"),
	KeyCode.from_char("I"),
	KeyCode.from_char("J"),
	KeyCode.from_char("K"),
	KeyCode.from_char("L"),
	KeyCode.from_char("M"),
	KeyCode.from_char("N"),
	KeyCode.from_char("O"),
	KeyCode.from_char("P"),
	KeyCode.from_char("Q"),
	KeyCode.from_char("R"),
	KeyCode.from_char("S"),
	KeyCode.from_char("T"),
	KeyCode.from_char("U"),
	KeyCode.from_char("V"),
	KeyCode.from_char("W"),
	KeyCode.from_char("X"),
	KeyCode.from_char("Y"),
	KeyCode.from_char("Z"),
#numbers
	KeyCode.from_char("0"),
	KeyCode.from_char("1"),
	KeyCode.from_char("2"),
	KeyCode.from_char("3"),
	KeyCode.from_char("4"),
	KeyCode.from_char("5"),
	KeyCode.from_char("6"),
	KeyCode.from_char("7"),
	KeyCode.from_char("8"),
	KeyCode.from_char("9"),
#symbols
	KeyCode.from_char("!"),
	KeyCode.from_char("@"),
	KeyCode.from_char("#"),
	KeyCode.from_char("$"),
	KeyCode.from_char("%"),
	KeyCode.from_char("^"),
	KeyCode.from_char("&"),
	KeyCode.from_char("*"),
	KeyCode.from_char("("),
	KeyCode.from_char(")"),
	KeyCode.from_char("-"),
	KeyCode.from_char("_"),
	KeyCode.from_char("+"),
	KeyCode.from_char("="),
	KeyCode.from_char("{"),
	KeyCode.from_char("["),
	KeyCode.from_char("}"),
	KeyCode.from_char("]"),
	KeyCode.from_char("|"),
	KeyCode.from_char("\\"),
	KeyCode.from_char(";"),
	KeyCode.from_char(":"),
	KeyCode.from_char("'"),
	KeyCode.from_char("\""),
	KeyCode.from_char("),"),
	KeyCode.from_char("<"),
	KeyCode.from_char("."),
	KeyCode.from_char(">"),
	KeyCode.from_char("/"),
	KeyCode.from_char("?"),
	KeyCode.from_char("`"),
	KeyCode.from_char("~"),
#function keys
	Key.f1,
	Key.f2,
	Key.f3,
	Key.f4,
	Key.f5,
	Key.f6,
	Key.f7,
	Key.f8,
	Key.f9,
	Key.f10,
	Key.f11,
	Key.f12,
#Arrow keys
	Key.up,
	Key.down,
	Key.left,
	Key.right,
#Modifier keys
	Key.ctrl,
	Key.ctrl_r,
	Key.cmd,
	Key.cmd_r,
	Key.alt,
	Key.alt_r,
	Key.num_lock,
	Key.caps_lock,
	Key.shift,
	Key.shift_r,
#Macro keys
	Key.enter,
	Key.backspace,
	Key.delete,
	Key.home,
	Key.end,
	Key.insert,
	Key.page_up,
	Key.page_down,
	Key.esc,
]