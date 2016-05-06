# planet-hunters-image-generator

Example usage:

```
docker run -it --rm -v $PWD:/out/ zooniverse/planet-hunters-image-generator ./generate.py /out/files.dat
```

Where `files.dat` contains space-separated values, with a header row containing
at least the columns "datalocation", "userxmin", "userxmax" (other columns are
ignored).
