create table
  public.qadocuments_bge (
    id uuid not null,
    question_content text null,
    answer_content text null,
    metadata jsonb null,
    question_embedding public.vector null,
    answer_embedding public.vector null,
    constraint qadocuments_bge_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.qadocuments_bge_guides (
    id uuid not null,
    question_content text null,
    answer_content text null,
    metadata jsonb null,
    question_embedding public.vector null,
    answer_embedding public.vector null,
    constraint qadocuments_bge_guides_pkey primary key (id)
  ) tablespace pg_default;



#match_qadocuments_bge_guides_a
BEGIN
    RETURN QUERY
    SELECT
        q.id,
        q.question_content, -- corresponds to Document.pageContent
        q.answer_content,
        q.metadata,
        1 - (q.answer_embedding <=> query_embedding) AS similarity
    FROM QAdocuments_bge_guides q
    WHERE q.metadata @> filter
    ORDER BY q.answer_embedding <=> query_embedding
    LIMIT match_count;
END;



#match_qadocuments_bge_guides_q
  SELECT
    id,
    question_content, -- corresponds to Document.pageContent
    answer_content,
    metadata,
    1 - (QAdocuments_bge_guides.question_embedding <=> query_embedding) AS similarity
  FROM QAdocuments_bge_guides
  WHERE metadata @> filter
  ORDER BY QAdocuments_bge_guides.question_embedding <=> query_embedding
  LIMIT match_count
