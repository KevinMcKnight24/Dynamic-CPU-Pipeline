.PHONY: clean test

test: 431Project1.py test.in
	env python3 431Project1.py test.in > out.txt

clean:
	-rm out.txt
