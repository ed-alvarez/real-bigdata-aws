-- Not implemented yet. Doesn't support query parameters so prone to
-- potential SQL injection - though firm_identifier is internally supplied.
CREATE OR REPLACE FUNCTION slack_ids(fingerprint_firm_identifier varchar(255))
  RETURNS TABLE(firm_name VARCHAR(255)
              , firm_identifier VARCHAR(255)
              , assignment_name VARCHAR(255)
              , first_name VARCHAR(30)
              , last_name VARCHAR(150)
              , email VARCHAR(254)
              , slack_id VARCHAR(50) ) AS
$func$
BEGIN
  RETURN QUERY
        SELECT ff.firm_name,
               ff.firm_identifier,
               ffa.assignment_name,
               -- ffa.fingerprint_user_id,
               fu.first_name,
               fu.last_name,
               fu.email,
               fu.slack_id
        FROM main_fingerprintfirm ff,
             main_fingerprintfirmassignment ffa,
             main_fingerprintuser fu
        WHERE ff.id = ffa.fingerprint_firm_id
              and ffa.fingerprint_user_id = fu.id
              and ff.firm_identifier = fingerprint_firm_identifier
              --and fu.slack_id is not null
              ;
END;
$func$  LANGUAGE plpgsql;
