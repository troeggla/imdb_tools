#!/bin/bash

if [ -z "$1" ]; then
  echo "USAGE: $0 [search_term | imdb_id] [seasons]"
  exit 1
fi

is_imdb_id=`echo $1 |egrep -o "^tt[0-9]+$"`

if [ -z "$is_imdb_id" ]; then
  echo "Searching for \"$1\"..."
  imdb_id=`python get_imdb_id.py "$1" |head -n1 |cut -d" " -f1`
else
  imdb_id=$1
fi

echo "Plotting regression for ${imdb_id}..."
python ratings_regression.py $imdb_id $2
