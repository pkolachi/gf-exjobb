sed  "s/('\([^']*\)', '\([^']*\)')/\1/g" | sed  "s/(\"\([^\"]*\)\", '\([^']*\)')/\1/g" | sed  "s/(\"\([^\"]*\)\", \"\([^\"]*\)\")/\1/g" | sed  "s/(\'\([^\']*\)\', \"\([^\"]*\)\")/\1/g"
