"""The literature candidate index and extraction guidance stay aligned."""

import csv
from pathlib import Path


VALIDATION = Path(__file__).resolve().parents[1] / 'validation'


def rows(name):
    with (VALIDATION / name).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def test_literature_candidates_have_unique_ids_and_matching_extraction_notes():
    papers = rows('literature_tpd_candidates.csv')
    notes = rows('literature_extraction_notes.csv')
    assert len(papers) >= 20
    publication_ids = [paper['id'] for paper in papers]
    note_ids = [entry['id'] for entry in notes]
    assert len(publication_ids) == len(set(publication_ids))
    assert len(note_ids) == len(set(note_ids))
    assert set(publication_ids) == set(note_ids)
    assert all(paper['title'].strip() and paper['url'].strip()
               and paper['digitization_status'].strip() for paper in papers)
    assert all(entry['where_to_find_data'].strip() and entry['what_to_extract'].strip()
               and entry['critical_metadata'].strip() for entry in notes)


def test_unextracted_sources_are_not_claimed_as_experimental_validation():
    papers = rows('literature_tpd_candidates.csv')
    known_statuses = {'not_started', 'source_inspected', 'data_located',
                      'digitized', 'excluded', 'validated'}
    assert all(paper['digitization_status'] in known_statuses for paper in papers)
    assert all(paper['outreach_status'] in {'not_contacted', 'sent', 'replied',
                                          'declined', 'bounced'} for paper in papers)
    # A future change to 'validated' must have trace-level evidence added and
    # this assertion deliberately revisited before anyone cites it in a paper.
    assert not [paper for paper in papers if paper['digitization_status'] == 'validated']


def test_first_benchmark_plan_does_not_imply_that_extraction_was_completed():
    guide = (VALIDATION / 'FIRST_EXPERIMENTAL_BENCHMARK.md').read_text(encoding='utf-8')
    assert all(identifier in guide for identifier in ('LIT001', 'LIT002', 'LIT003'))
    assert 'Time_ms,Signal,Temperature' in guide
    assert 'derived from an assumed linear heating program' in guide
    assert 'never measured acquisition time' in guide
    assert 'not a' in guide.lower() or 'do not call' in guide.lower()
