main:
	make makedirs
	make sort
	make fix
	make build

makedirs:
	mkdir -p sorted
	mkdir -p inputs
	mkdir -p indexfiles

sort:
	sort -u original/reviews.txt > sorted/reviews.txt
	sort -u original/scores.txt > sorted/scores.txt
	sort -u original/pterms.txt > sorted/pterms.txt
	sort -u original/rterms.txt > sorted/rterms.txt

fix: 
	perl fix.pl < sorted/reviews.txt > inputs/reviews.txt
	perl fix.pl < sorted/scores.txt > inputs/scores.txt
	perl fix.pl < sorted/pterms.txt > inputs/pterms.txt
	perl fix.pl < sorted/rterms.txt > inputs/rterms.txt

build:
	db_load -T -t hash indexfiles/rw.idx < inputs/reviews.txt
	db_load -c duplicates=1 -T -t btree indexfiles/pt.idx < inputs/pterms.txt
	
	db_load -c duplicates=1 -T -t btree indexfiles/rt.idx < inputs/rterms.txt
	db_load -c duplicates=1 -T -t btree indexfiles/sc.idx < inputs/scores.txt

clean:
	rm -f inputs
	rm -f indexfiles
	rm -f sorted
