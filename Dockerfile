FROM python
RUN pip install scrapy
RUN pip install crochet
RUN pip install flask
RUN pip install -U flask-cors
RUN pip install requests
RUN pip install fuzzywuzzy
RUN pip install python-Levenshtein
RUN pip pip install elastic-enterprise-search
RUN pip install elastic-app-search
RUN pip install selenium
WORKDIR C:/workspace/pyenv/Scrapping
COPY ./ /app/scrapping
EXPOSE 5000
WORKDIR /app/scrapping
CMD ["/app/scrapping/main.py"]
ENTRYPOINT ["python"]