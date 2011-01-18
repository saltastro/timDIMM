for i in `ls | grep 2011`; do foo=`echo $i | cut -c 5-8`; mv $i $foo; done
